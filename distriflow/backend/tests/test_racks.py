from contextlib import contextmanager
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from tests.test_access import client, login
from app.core.commands import AuditLog
from app.core.database import get_db
from app.main import app
from app.modules.catalog.models import StorageLocation
from app.modules.inventory.models import BalanceLocation, InventoryBalance
from app.modules.inventory.rack_service import coordinates, location_code

PATH = "/api/v1/inventory/rack-map"
BODY = {"warehouse_id": "WH", "total_positions": 800}


@contextmanager
def database():
    generator = app.dependency_overrides[get_db]()
    try:
        yield next(generator)
    finally:
        generator.close()


def initialize(client):
    headers = login(client, "admin")
    response = client.post(PATH + "/initialize", headers=headers, json=BODY)
    assert response.status_code == 200, response.text
    return headers, response


def test_layout_contains_exactly_800_unique_single_positions():
    coords = list(coordinates())
    assert len(coords) == len(set(coords)) == 800
    assert len({location_code(*coord) for coord in coords}) == 800
    assert {coord[2] for coord in coords} == set(range(1, 11))
    assert len([coord for coord in coords if coord[0] == 1]) == 100


def test_initial_map_does_not_invent_locations_or_stock(client):
    login(client, "admin")
    result = client.get(PATH).json()
    assert result["layout"]["totalPositions"] == 800
    assert result["locations"] == []
    assert result["otherLocationCount"] == 1
    assert result["unmappedBalanceCount"] == 1


def test_initialize_is_persistent_idempotent_and_preserves_existing_data(client):
    headers, response = initialize(client)
    assert response.json()["created"] == 800
    assert (
        client.post(PATH + "/initialize", headers=headers, json=BODY).json()
        == response.json()
    )
    again = client.post(
        PATH + "/initialize",
        headers={**headers, "Idempotency-Key": "new-setup-key"},
        json=BODY,
    )
    assert again.json()["created"] == 0
    data = client.get(PATH).json()
    assert len(data["locations"]) == 800
    assert all(l["status"] == "empty" and l["items"] == [] for l in data["locations"])
    with database() as db:
        assert db.scalar(select(func.count()).select_from(StorageLocation)) == 801
        assert db.get(StorageLocation, "location-a").code == "A-01"
        assert db.get(InventoryBalance, "balance-a").on_hand == 10
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "rack.initialize.single")
            )
            == 2
        )


@pytest.mark.parametrize("role", ["supplier", "retailer", "dispatch", "shipper"])
def test_partner_dispatch_and_shipper_cannot_read_full_map_or_create_positions(
    client, role
):
    headers = login(client, role)
    assert client.get(PATH).status_code == 403
    assert (
        client.post(PATH + "/initialize", headers=headers, json=BODY).status_code == 403
    )


def test_setup_requires_csrf_key_exact_capacity_and_own_warehouse(client):
    headers = login(client, "admin")
    assert client.post(PATH + "/initialize", json=BODY).status_code == 403
    assert (
        client.post(
            PATH + "/initialize",
            headers={"X-CSRF-Token": headers["X-CSRF-Token"]},
            json=BODY,
        ).status_code
        == 400
    )
    assert (
        client.post(
            PATH + "/initialize",
            headers=headers,
            json={**BODY, "total_positions": 1600},
        ).status_code
        == 422
    )
    assert (
        client.post(
            PATH + "/initialize", headers=headers, json={**BODY, "warehouse_id": "WH-B"}
        ).status_code
        == 404
    )
    with database() as db:
        assert db.scalar(select(func.count()).select_from(StorageLocation)) == 1


def test_single_map_reads_recorded_stock_without_leaking_foreign_warehouse(
    client,
):
    initialize(client)
    with database() as db:
        front = db.scalar(
            select(StorageLocation).where(
                StorageLocation.code == location_code(1, 1, 1)
            )
        )
        db.add(BalanceLocation(balance_id="balance-a", location_id=front.id))
        db.add(
            InventoryBalance(
                id="foreign-rack-stock",
                owner_id="retailer-b",
                sku_code="SKU-B",
                warehouse_id="WH-B",
                on_hand=99,
            )
        )
        db.commit()
    data = client.get(PATH).json()
    front = next(l for l in data["locations"] if l["code"] == location_code(1, 1, 1))
    adjacent = next(l for l in data["locations"] if l["code"] == location_code(1, 1, 2))
    assert front["status"] == "reserved"
    assert front["items"][0]["onHand"] == 10
    assert front["items"][0]["reserved"] == 3
    assert front["items"][0]["available"] == 7
    assert adjacent["status"] == "empty"
    assert all(
        "frontRecordedOccupied" not in l and "depth" not in l for l in data["locations"]
    )
    assert front["column"] == 1
    assert data["unmappedBalanceCount"] == 0
    assert all(i["skuCode"] != "SKU-B" for l in data["locations"] for i in l["items"])


def test_conflicting_existing_code_aborts_without_overwriting_or_partial_setup(client):
    headers = login(client, "admin")
    with database() as db:
        db.add(
            StorageLocation(
                id="legacy-conflict", warehouse_id="WH", code=location_code(1, 1, 1)
            )
        )
        db.commit()
    assert (
        client.post(PATH + "/initialize", headers=headers, json=BODY).status_code == 409
    )
    with database() as db:
        assert db.scalar(select(func.count()).select_from(StorageLocation)) == 2
        assert db.get(StorageLocation, "legacy-conflict").rack_row is None


@pytest.mark.parametrize(
    "coord", [(1, None, 1, 1), (9, 1, 1, 1), (1, 11, 1, 1), (1, 1, 11, 1), (1, 1, 1, 2)]
)
def test_database_rejects_partial_or_out_of_range_coordinates(client, coord):
    with database() as db:
        db.add(
            StorageLocation(
                warehouse_id="WH",
                code="invalid",
                rack_row=coord[0],
                rack_level=coord[1],
                rack_bay=coord[2],
                rack_depth=coord[3],
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_database_rejects_duplicate_coordinate_even_with_different_code(client):
    with database() as db:
        for code in ("same-coordinate-1", "same-coordinate-2"):
            db.add(
                StorageLocation(
                    warehouse_id="WH",
                    code=code,
                    rack_row=1,
                    rack_level=1,
                    rack_bay=1,
                    rack_depth=1,
                )
            )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_postgres_migration_preserves_ids_codes_and_stock_links(client, monkeypatch):
    import importlib
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    migration = importlib.import_module("migrations.versions.20261126_03_single_racks")
    with database() as db:
        if db.get_bind().dialect.name != "postgresql":
            pytest.skip(
                "Migration with existing stock references is verified on PostgreSQL"
            )
        operations = Operations(MigrationContext.configure(db.connection()))
        operations.drop_constraint(
            "ck_storage_rack_coordinate", "storage_locations", type_="check"
        )
        operations.create_check_constraint(
            "ck_storage_rack_coordinate", "storage_locations", migration.DOUBLE_CHECK
        )
        for location_id, bay, depth in [("old-back", 1, 2), ("old-next-front", 2, 1)]:
            db.add(
                StorageLocation(
                    id=location_id,
                    code=location_id,
                    warehouse_id="WH",
                    rack_row=1,
                    rack_level=1,
                    rack_bay=bay,
                    rack_depth=depth,
                )
            )
        db.flush()
        db.add(BalanceLocation(balance_id="balance-a", location_id="old-back"))
        db.flush()
        monkeypatch.setattr(migration, "op", operations)
        migration.upgrade()
        db.expire_all()
        assert db.get(StorageLocation, "old-back").rack_bay == 2
        assert db.get(StorageLocation, "old-next-front").rack_bay == 3
        assert db.get(StorageLocation, "old-back").rack_depth == 1
        assert db.get(StorageLocation, "old-back").code == "old-back"
        assert db.get(BalanceLocation, "balance-a").location_id == "old-back"
        assert db.get(InventoryBalance, "balance-a").on_hand == 10
        db.commit()

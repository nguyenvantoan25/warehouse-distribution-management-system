import pytest
import os
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.modules.auth.access import password_hash
from app.modules.auth.models import User
from app.modules.dispatch.models import Package, PickupTask
from app.modules.inventory.models import InventoryBalance, Warehouse, StockReservation
from app.modules.catalog.models import (
    Organization,
    Sku,
    PartnerMembership,
    SupplyRelationship,
    StorageLocation,
)
from app.modules.handover.models import Receipt


@pytest.fixture
def client(request):
    test_url = os.getenv("TEST_DATABASE_URL")
    if test_url:
        url = make_url(test_url)
        if (
            url.get_backend_name() != "postgresql"
            or url.database != "distriflow_module_tests"
        ):
            raise ValueError(
                "PostgreSQL tests require the dedicated distriflow_module_tests database"
            )
        schema = "test_" + uuid.uuid4().hex
        admin_engine = create_engine(url)
        with admin_engine.begin() as connection:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})

        def cleanup():
            engine.dispose()
            with admin_engine.begin() as connection:
                connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
            admin_engine.dispose()

        request.addfinalizer(cleanup)
    else:
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        for name, role in [
            ("admin", "WAREHOUSE_ADMIN"),
            ("dispatch", "DISPATCH_MANAGER"),
            ("shipper", "SHIPPER"),
            ("other", "SHIPPER"),
            ("supplier", "SUPPLIER"),
            ("retailer", "RETAILER_OWNER"),
            ("retailer-b", "RETAILER_OWNER"),
        ]:
            db.add(
                User(
                    id=name,
                    username=name,
                    role=role,
                    password_hash=password_hash("test-password"),
                    warehouse_scope="Kho A",
                )
            )
        db.add_all(
            [
                Warehouse(id="WH", name="Kho A"),
                Warehouse(id="WH-B", name="Kho B"),
                Organization(id="retailer-a", name="Owner A", kind="RETAILER"),
                Organization(id="retailer-b", name="Owner B", kind="RETAILER"),
                Organization(id="supplier-a", name="Supplier A", kind="SUPPLIER"),
            ]
        )
        db.flush()
        db.add_all(
            [
                Sku(
                    id="sku-a",
                    code="SKU",
                    name="Product A",
                    owner_id="retailer-a",
                    base_unit="chiếc",
                ),
                Sku(
                    id="sku-b",
                    code="SKU-B",
                    name="Product B",
                    owner_id="retailer-b",
                    base_unit="chiếc",
                ),
                PartnerMembership(user_id="supplier", organization_id="supplier-a"),
                PartnerMembership(user_id="retailer", organization_id="retailer-a"),
                PartnerMembership(user_id="retailer-b", organization_id="retailer-b"),
                StorageLocation(id="location-a", warehouse_id="WH", code="A-01"),
            ]
        )
        db.flush()
        db.add_all(
            [
                SupplyRelationship(
                    supplier_id="supplier-a", owner_id="retailer-a", sku_id="sku-a"
                ),
                SupplyRelationship(
                    supplier_id="supplier-a", owner_id="retailer-b", sku_id="sku-b"
                ),
            ]
        )
        db.add_all(
            [
                PickupTask(
                    id="assigned",
                    code="T1",
                    warehouse_name="Kho A",
                    shipper_id="shipper",
                ),
                PickupTask(
                    id="foreign", code="T2", warehouse_name="Kho B", shipper_id="other"
                ),
            ]
        )
        db.flush()
        db.add(Package(id="p1", task_id="assigned", code="P1"))
        db.add(
            InventoryBalance(
                id="balance-a",
                owner_id="retailer-a",
                sku_code="SKU",
                warehouse_id="WH",
                on_hand=10,
                reserved=3,
                unavailable=0,
            )
        )
        db.flush()
        db.add(StockReservation(task_id="assigned", balance_id="balance-a", quantity=3))
        db.commit()

    def override_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def login(client, name):
    response = client.post(
        "/api/v1/auth/login", json={"username": name, "password": "test-password"}
    )
    assert response.status_code == 200
    assert "HttpOnly" in response.headers["set-cookie"]
    return {"X-CSRF-Token": response.json()["csrfToken"], "Idempotency-Key": "test-key"}


def test_headers_cannot_impersonate_user(client):
    assert (
        client.get(
            "/api/v1/dashboard", headers={"X-Demo-Actor": "warehouse-admin-demo"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login", json={"username": "admin", "password": "wrong"}
        ).status_code
        == 401
    )


def test_shipper_access_and_record_scope(client):
    headers = login(client, "shipper")
    assert client.get("/api/v1/dashboard").status_code == 403
    assert [x["id"] for x in client.get("/api/v1/pickup-tasks").json()] == ["assigned"]
    assert (
        client.post(
            "/api/v1/pickup-tasks/foreign/respond",
            headers=headers,
            json={"version": 1, "accepted": True},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/warehouse-confirm",
            headers=headers,
            json={"version": 1},
        ).status_code
        == 403
    )


def test_dispatch_read_only_and_warehouse_scope(client):
    headers = login(client, "dispatch")
    assert [x["id"] for x in client.get("/api/v1/dashboard").json()["tasks"]] == [
        "assigned"
    ]
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/warehouse-confirm",
            headers=headers,
            json={"version": 1},
        ).status_code
        == 403
    )
    login(client, "admin")
    assert [x["id"] for x in client.get("/api/v1/pickup-tasks").json()] == ["assigned"]


def test_csrf_logout_revocation_and_disabled_account(client):
    headers = login(client, "shipper")
    cookie = client.cookies.get("distriflow_session")
    assert client.post("/api/v1/auth/logout").status_code == 403
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    assert (
        client.get(
            "/api/v1/auth/me", headers={"Cookie": f"distriflow_session={cookie}"}
        ).status_code
        == 401
    )
    login(client, "shipper")
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    db.get(User, "shipper").active = False
    db.commit()
    generator.close()
    assert client.get("/api/v1/auth/me").status_code == 401


def test_authenticated_handover_and_retry(client):
    headers = login(client, "shipper")
    version = 1
    for i, (action, payload) in enumerate(
        [
            ("respond", {"accepted": True}),
            ("arrive", {}),
            ("scan", {"package_code": "P1"}),
            ("shipper-confirm", {}),
        ]
    ):
        result = client.post(
            f"/api/v1/pickup-tasks/assigned/{action}",
            headers={**headers, "Idempotency-Key": f"step-{i}"},
            json={"version": version, **payload},
        )
        assert result.status_code == 200, result.text
        version = result.json()["version"]
    headers = login(client, "admin")
    for _ in range(2):
        result = client.post(
            "/api/v1/pickup-tasks/assigned/warehouse-confirm",
            headers=headers,
            json={"version": version},
        )
        assert result.status_code == 200, result.text
        assert result.json()["status"] == "handed_over"


def test_dispatch_assignment_scope_version_and_shipper_identity(client):
    headers = login(client, "dispatch")
    assert client.get("/api/v1/shippers").status_code == 200
    assert (
        client.post(
            "/api/v1/pickup-tasks/foreign/assign",
            headers=headers,
            json={"version": 1, "shipper_id": "other"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/assign",
            headers=headers,
            json={"version": 99, "shipper_id": "other"},
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/assign",
            headers=headers,
            json={"version": 1, "shipper_id": "admin"},
        ).status_code
        == 422
    )
    response = client.post(
        "/api/v1/pickup-tasks/assigned/assign",
        headers=headers,
        json={"version": 1, "shipper_id": "other"},
    )
    assert response.status_code == 200
    assert response.json()["shipperId"] == "other"
    old_shipper = login(client, "shipper")
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/respond",
            headers=old_shipper,
            json={"version": 2, "accepted": True},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/assign",
            headers=old_shipper,
            json={"version": 2, "shipper_id": "shipper"},
        ).status_code
        == 403
    )


def test_cannot_assign_after_shipper_acceptance(client):
    headers = login(client, "shipper")
    response = client.post(
        "/api/v1/pickup-tasks/assigned/respond",
        headers=headers,
        json={"version": 1, "accepted": True},
    )
    assert response.status_code == 200
    headers = login(client, "dispatch")
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/assign",
            headers=headers,
            json={"version": 2, "shipper_id": "other"},
        ).status_code
        == 409
    )


def test_dashboard_flow_uses_only_scoped_receipts_in_last_30_days(client):
    from datetime import datetime, timedelta

    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    db.add(
        PickupTask(id="old", code="OLD", warehouse_name="Kho A", shipper_id="shipper")
    )
    db.flush()
    db.add_all(
        [
            Receipt(task_id="assigned", number="R1", issued_at=datetime.utcnow()),
            Receipt(task_id="foreign", number="R2", issued_at=datetime.utcnow()),
            Receipt(
                task_id="old",
                number="R3",
                issued_at=datetime.utcnow() - timedelta(days=40),
            ),
            Package(task_id="old", code="OLD-PACKAGE"),
        ]
    )
    db.commit()
    generator.close()
    login(client, "dispatch")
    flow = client.get("/api/v1/dashboard").json()["flow"]
    assert len(flow) == 30
    assert sum(day["quantity"] for day in flow) == 1
    assert flow == sorted(flow, key=lambda day: day["date"])

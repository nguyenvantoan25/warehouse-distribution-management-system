import uuid
from sqlalchemy import select, func
from tests.test_access import client, login
from app.core.database import get_db
from app.main import app
from app.modules.inventory.models import InventoryPosting, StockReservation
from app.modules.handover.models import Receipt, HandoverConfirmation
from app.modules.outbound.models import PackageItem
from app.modules.catalog.models import Organization


def test_inactive_owner_cannot_receive_new_documents(client):
    generator = app.dependency_overrides[get_db]()
    with next(generator) as db:
        db.get(Organization, "retailer-a").active = False
        db.commit()
    generator.close()
    headers = login(client, "supplier")
    post(
        client,
        headers,
        "/inbound-requests",
        {
            "supplier_id": "supplier-a",
            "owner_id": "retailer-a",
            "warehouse_id": "WH",
            "lines": [{"sku_id": "sku-a", "quantity": 1}],
        },
        422,
    )


def post(client, headers, path, body, status=200, key=None):
    response = client.post(
        "/api/v1" + path,
        headers={**headers, "Idempotency-Key": key or str(uuid.uuid4())},
        json=body,
    )
    assert response.status_code == status, response.text
    return response.json()


def totals(client):
    values = client.get("/api/v1/inventory/balances").json()
    return {
        field: sum(row[field] for row in values)
        for field in ["onHand", "reserved", "unavailable", "available"]
    }


def test_supplier_to_retailer_to_handover_full_workflow(client):
    headers = login(client, "supplier")
    inbound = post(
        client,
        headers,
        "/inbound-requests",
        {
            "supplier_id": "supplier-a",
            "owner_id": "retailer-a",
            "warehouse_id": "WH",
            "lines": [{"sku_id": "sku-a", "quantity": 100}],
        },
        201,
    )
    assert client.get("/api/v1/inventory/balances").status_code == 403
    login(client, "retailer-b")
    assert client.get("/api/v1/outbound-requests").json() == []
    assert client.get("/api/v1/inventory/balances").json() == []
    headers = login(client, "admin")
    assert totals(client)["onHand"] == 10
    assert any(
        log["action"] == "inbound.create" and log["objectId"] == inbound["id"]
        for log in client.get("/api/v1/audit-logs").json()
    )
    inbound = post(
        client,
        headers,
        f'/inbound-requests/{inbound["id"]}/review',
        {"version": inbound["version"], "accepted": True},
    )
    inbound = post(
        client,
        headers,
        f'/inbound-requests/{inbound["id"]}/receive',
        {
            "version": inbound["version"],
            "lines": [
                {"line_id": inbound["lines"][0]["id"], "good": 90, "quarantined": 10}
            ],
            "note": "10 hàng hỏng cần cách ly",
        },
    )
    assert totals(client)["onHand"] == 10
    inbound = post(
        client,
        headers,
        f'/inbound-requests/{inbound["id"]}/putaway',
        {"version": inbound["version"], "location_id": "location-a"},
    )
    assert inbound["status"] == "stocked"
    assert totals(client) == {
        "onHand": 110,
        "reserved": 3,
        "unavailable": 10,
        "available": 97,
    }
    headers = login(client, "retailer")
    outbound = post(
        client,
        headers,
        "/outbound-requests",
        {
            "owner_id": "retailer-a",
            "warehouse_id": "WH",
            "lines": [{"sku_id": "sku-a", "quantity": 25}],
        },
        201,
    )
    assert totals(client)["reserved"] == 3
    headers = login(client, "admin")
    for action in ["approve", "pick"]:
        outbound = post(
            client,
            headers,
            f'/outbound-requests/{outbound["id"]}/{action}',
            {"version": outbound["version"]},
        )
    assert totals(client) == {
        "onHand": 110,
        "reserved": 28,
        "unavailable": 10,
        "available": 72,
    }
    outbound = post(
        client,
        headers,
        f'/outbound-requests/{outbound["id"]}/pack',
        {"version": outbound["version"], "package_count": 3},
    )
    task = next(
        t
        for t in client.get("/api/v1/pickup-tasks").json()
        if t["id"] == outbound["taskId"]
    )
    assert len(task["packages"]) == 3
    assert totals(client)["onHand"] == 110
    headers = login(client, "dispatch")
    task = post(
        client,
        headers,
        f'/pickup-tasks/{task["id"]}/assign',
        {"version": task["version"], "shipper_id": "shipper"},
    )
    headers = login(client, "shipper")
    for action in ["respond", "arrive"]:
        task = post(
            client,
            headers,
            f'/pickup-tasks/{task["id"]}/{action}',
            {
                "version": task["version"],
                **({"accepted": True} if action == "respond" else {}),
            },
        )
    for code in task["packages"]:
        task = post(
            client,
            headers,
            f'/pickup-tasks/{task["id"]}/scan',
            {"version": task["version"], "package_code": code},
        )
    task = post(
        client,
        headers,
        f'/pickup-tasks/{task["id"]}/shipper-confirm',
        {"version": task["version"]},
    )
    assert task["status"] == "pending_confirmations"
    headers = login(client, "admin")
    assert totals(client)["onHand"] == 110
    payload = {"version": task["version"]}
    key = str(uuid.uuid4())
    result = post(
        client,
        headers,
        f'/pickup-tasks/{task["id"]}/warehouse-confirm',
        payload,
        key=key,
    )
    assert (
        post(
            client,
            headers,
            f'/pickup-tasks/{task["id"]}/warehouse-confirm',
            payload,
            key=key,
        )
        == result
    )
    assert result["status"] == "handed_over"
    assert totals(client) == {
        "onHand": 85,
        "reserved": 3,
        "unavailable": 10,
        "available": 72,
    }
    receipt = client.get(f'/api/v1/pickup-tasks/{task["id"]}/receipt').json()
    assert sum(line["quantity"] for line in receipt["stockIssues"]) == 25
    assert len({c["version"] for c in receipt["confirmations"]}) == 1
    assert (
        sum(day["quantity"] for day in client.get("/api/v1/dashboard").json()["flow"])
        == 3
    )
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    assert (
        db.scalar(select(func.count(Receipt.id)).where(Receipt.task_id == task["id"]))
        == 1
    )
    assert (
        db.scalar(
            select(func.sum(InventoryPosting.quantity)).where(
                InventoryPosting.task_id == task["id"]
            )
        )
        == 25
    )
    assert db.scalar(select(func.sum(PackageItem.quantity))) == 25
    generator.close()


def test_reservations_compete_and_cancel_releases_only_its_own_stock(client):
    headers = login(client, "retailer")
    docs = [
        post(
            client,
            headers,
            "/outbound-requests",
            {
                "owner_id": "retailer-a",
                "warehouse_id": "WH",
                "lines": [{"sku_id": "sku-a", "quantity": 6}],
            },
            201,
        )
        for _ in range(2)
    ]
    headers = login(client, "admin")
    first = post(
        client, headers, f'/outbound-requests/{docs[0]["id"]}/approve', {"version": 1}
    )
    post(
        client,
        headers,
        f'/outbound-requests/{docs[1]["id"]}/approve',
        {"version": 1},
        409,
    )
    assert totals(client)["reserved"] == 9
    post(
        client,
        headers,
        f'/outbound-requests/{first["id"]}/cancel',
        {"version": first["version"]},
    )
    assert totals(client)["reserved"] == 3
    post(
        client,
        headers,
        "/inventory/holds",
        {"balance_id": "balance-a", "quantity": 8, "reason": "test hold"},
        409,
    )
    post(
        client,
        headers,
        "/inventory/holds",
        {"balance_id": "balance-a", "quantity": 2, "reason": "test hold"},
    )
    assert totals(client)["available"] == 5
    post(
        client,
        headers,
        "/inventory/holds",
        {
            "balance_id": "balance-a",
            "quantity": 2,
            "release": True,
            "reason": "release hold",
        },
    )
    assert totals(client)["available"] == 7


def test_command_retry_is_bound_to_action_and_payload(client):
    headers = login(client, "shipper")
    key = str(uuid.uuid4())
    body = {"version": 1, "accepted": True}
    first = post(client, headers, "/pickup-tasks/assigned/respond", body, key=key)
    assert (
        post(client, headers, "/pickup-tasks/assigned/respond", body, key=key) == first
    )
    post(client, headers, "/pickup-tasks/assigned/arrive", {"version": 2}, 409, key=key)
    assert not client.get("/api/v1/pickup-tasks/assigned").json()["arrivedAtWarehouse"]


def test_missing_reservation_never_posts_receipt_or_finalizes(client):
    headers = login(client, "shipper")
    task = post(
        client,
        headers,
        "/pickup-tasks/assigned/respond",
        {"version": 1, "accepted": True},
    )
    task = post(
        client, headers, "/pickup-tasks/assigned/arrive", {"version": task["version"]}
    )
    task = post(
        client,
        headers,
        "/pickup-tasks/assigned/scan",
        {"version": task["version"], "package_code": "P1"},
    )
    task = post(
        client,
        headers,
        "/pickup-tasks/assigned/shipper-confirm",
        {"version": task["version"]},
    )
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    reservation = db.scalar(
        select(StockReservation).where(StockReservation.task_id == "assigned")
    )
    reservation.quantity = 50
    db.commit()
    generator.close()
    headers = login(client, "admin")
    post(
        client,
        headers,
        "/pickup-tasks/assigned/warehouse-confirm",
        {"version": task["version"]},
        409,
    )
    assert (
        client.get("/api/v1/pickup-tasks/assigned").json()["status"]
        == "pending_confirmations"
    )
    assert totals(client)["onHand"] == 10
    assert client.get("/api/v1/pickup-tasks/assigned/receipt").status_code == 409


def test_partner_cannot_forge_owner_or_supply_relationship(client):
    headers = login(client, "retailer-b")
    post(
        client,
        headers,
        "/outbound-requests",
        {
            "owner_id": "retailer-a",
            "warehouse_id": "WH",
            "lines": [{"sku_id": "sku-a", "quantity": 1}],
        },
        404,
    )
    headers = login(client, "supplier")
    post(
        client,
        headers,
        "/inbound-requests",
        {
            "owner_id": "retailer-a",
            "supplier_id": "supplier-a",
            "warehouse_id": "WH",
            "lines": [{"sku_id": "sku-b", "quantity": 1}],
        },
        422,
    )

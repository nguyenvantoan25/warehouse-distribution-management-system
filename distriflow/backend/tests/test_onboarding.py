from tests.test_access import client, login
from tests.test_workflow import post
from app.main import app
from app.core.database import get_db
from app.modules.auth.models import User


def test_first_warehouse_is_explicit_and_scoped(client):
    generator = app.dependency_overrides[get_db]()
    with next(generator) as db:
        db.get(User, "admin").warehouse_scope = ""
        db.commit()
    generator.close()
    headers = login(client, "admin")
    assert client.get("/api/v1/warehouses").json() == []
    result = post(
        client, headers, "/warehouses", {"name": "Kho người dùng khai báo"}, 201
    )
    assert result["name"] == "Kho người dùng khai báo"
    assert client.get("/api/v1/inventory/balances").json() == []
    assert client.get("/api/v1/warehouses").json() == [result]
    post(client, headers, "/warehouses", {"name": "Không được tạo kho thứ hai"}, 409)


def test_scope_management_never_grants_cross_warehouse_or_wrong_partner(client):
    headers = login(client, "retailer")
    assert client.get("/api/v1/accounts").status_code == 403
    headers = login(client, "admin")
    post(
        client,
        headers,
        "/accounts/supplier/scope",
        {"warehouse_id": "WH", "organization_id": "retailer-a"},
        422,
    )
    post(
        client,
        headers,
        "/accounts/supplier/scope",
        {"warehouse_id": "WH-B", "organization_id": "supplier-a"},
        404,
    )
    result = post(
        client,
        headers,
        "/accounts/supplier/scope",
        {"warehouse_id": "WH", "organization_id": "supplier-a"},
    )
    assert result["organizationIds"] == ["supplier-a"]
    assert "password_hash" not in result and "password" not in result

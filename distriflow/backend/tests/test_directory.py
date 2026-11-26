import json
import uuid
import pytest
from sqlalchemy import func, select
from tests.test_access import client, login
from tests.test_racks import database
from app.core.commands import AuditLog, CommandReceipt
from app.modules.auth.models import User
from app.modules.catalog.models import Organization, PartnerMembership, Sku
from app.modules.dispatch.models import PickupTask

PATH = "/api/v1/directory"
PASSWORD = "Directory-test-password-928"


def body(role="SUPPLIER"):
    return {
        "role": role,
        "username": "new-" + role.lower(),
        "name": "Tên do người dùng nhập",
        "password": PASSWORD,
        "supplied_goods": (
            "Loại hàng do người dùng nhập" if role == "SUPPLIER" else None
        ),
    }


def post(client, headers, path, data, code=200, key=None):
    response = client.post(
        path,
        headers={**headers, "Idempotency-Key": key or str(uuid.uuid4())},
        json=data,
    )
    assert response.status_code == code, response.text
    return response


@pytest.mark.parametrize("role", ["SHIPPER", "SUPPLIER", "RETAILER_OWNER"])
def test_create_edit_delete_each_group_and_revoke_sessions_without_exposing_password(
    client, role
):
    headers = login(client, "admin")
    admin_cookies = dict(client.cookies)
    request = body(role)
    created = post(client, headers, PATH, request, 201, "create-directory").json()
    assert created["role"] == role and created["name"] == request["name"]
    assert "password" not in created and "password_hash" not in created
    assert (
        post(client, headers, PATH, request, 201, "create-directory").json() == created
    )
    client.cookies.clear()
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": created["username"], "password": PASSWORD},
        ).status_code
        == 200
    )
    target_cookies = dict(client.cookies)
    client.cookies.clear()
    client.cookies.update(admin_cookies)
    update = {
        "version": created["version"],
        "name": "Tên đã chỉnh sửa",
        "username": created["username"],
        "supplied_goods": "Loại hàng đã sửa" if role == "SUPPLIER" else None,
        "password": PASSWORD + "-new",
    }
    edited = post(
        client, headers, PATH + "/" + created["id"] + "/update", update
    ).json()
    assert edited["version"] > created["version"]
    assert edited["name"] == "Tên đã chỉnh sửa"
    post(client, headers, PATH + "/" + created["id"] + "/update", update, 409)
    client.cookies.clear()
    client.cookies.update(target_cookies)
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": created["username"], "password": PASSWORD},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": created["username"], "password": PASSWORD + "-new"},
        ).status_code
        == 200
    )
    client.cookies.clear()
    client.cookies.update(admin_cookies)
    deleted = post(
        client,
        headers,
        PATH + "/" + created["id"] + "/delete",
        {"version": edited["version"]},
    ).json()
    assert deleted["deleted"] is True and deleted["active"] is False
    assert all(u["id"] != created["id"] for u in client.get(PATH).json()["accounts"])
    with database() as db:
        assert db.get(User, created["id"]) is not None
        if created["organizationId"]:
            org = db.get(Organization, created["organizationId"])
            assert org.name == "Tên đã chỉnh sửa" and org.active is False
            assert db.get(PartnerMembership, (created["id"], org.id)) is not None
        serialized = json.dumps(
            [a.before for a in db.scalars(select(AuditLog)).all()]
            + [a.after for a in db.scalars(select(AuditLog)).all()]
            + [r.response for r in db.scalars(select(CommandReceipt)).all()]
        )
        assert (
            PASSWORD not in serialized
            and "password_hash" not in serialized
            and "credentialDigest" not in serialized
        )


@pytest.mark.parametrize("role", ["supplier", "retailer", "shipper", "dispatch"])
def test_only_admin_manages_directory(client, role):
    headers = login(client, role)
    assert client.get(PATH).status_code == 403
    post(client, headers, PATH, body(), 403)
    post(client, headers, PATH + "/supplier/delete", {"version": 1}, 403)


def test_requires_csrf_key_valid_password_role_and_supplier_goods(client):
    assert client.get(PATH).status_code == 401
    headers = login(client, "admin")
    assert client.post(PATH, json=body()).status_code == 403
    assert (
        client.post(
            PATH, headers={"X-CSRF-Token": headers["X-CSRF-Token"]}, json=body()
        ).status_code
        == 400
    )
    for changes in [
        {"password": "short"},
        {"role": "WAREHOUSE_ADMIN"},
        {"supplied_goods": None},
        {"supplied_goods": "   "},
        {"name": "  "},
    ]:
        post(client, headers, PATH, {**body(), **changes}, 422)
    post(client, headers, PATH + "/admin/delete", {"version": 1}, 404)


def test_username_conflict_rolls_back_new_organization_and_preserves_existing_password(
    client,
):
    headers = login(client, "admin")
    with database() as db:
        original_hash = db.get(User, "supplier").password_hash
        before = db.scalar(select(func.count()).select_from(Organization))
    post(client, headers, PATH, {**body(), "username": "supplier"}, 409)
    with database() as db:
        assert db.scalar(select(func.count()).select_from(Organization)) == before
        assert db.get(User, "supplier").password_hash == original_hash


def test_cannot_manage_foreign_warehouse_or_change_role(client):
    headers = login(client, "admin")
    with database() as db:
        db.get(User, "supplier").warehouse_scope = "Kho B"
        db.commit()
    assert all(a["id"] != "supplier" for a in client.get(PATH).json()["accounts"])
    post(client, headers, PATH + "/supplier/delete", {"version": 1}, 404)
    post(
        client,
        headers,
        PATH + "/shipper/update",
        {
            "version": 1,
            "name": "Tên mới",
            "username": "shipper",
            "role": "WAREHOUSE_ADMIN",
        },
        422,
    )


def test_deletion_preserves_business_history_and_ownership(client):
    headers = login(client, "admin")
    listing = client.get(PATH).json()["accounts"]
    for user_id in ["shipper", "retailer"]:
        user = next(a for a in listing if a["id"] == user_id)
        post(
            client,
            headers,
            PATH + "/" + user_id + "/delete",
            {"version": user["version"]},
        )
    with database() as db:
        assert db.get(PickupTask, "assigned").shipper_id == "shipper"
        assert db.get(Sku, "sku-a").owner_id == "retailer-a"
        assert db.get(Organization, "retailer-a").active is False
    assert all(s["id"] != "shipper" for s in client.get("/api/v1/shippers").json())


def test_link_legacy_partner_explicitly_but_never_hijack_existing_membership(client):
    headers = login(client, "admin")
    post(client, headers, PATH, {**body(), "organization_id": "supplier-a"}, 409)
    with database() as db:
        db.add(Organization(id="orphan", name="Đối tác cũ", kind="SUPPLIER"))
        db.commit()
    assert any(o["id"] == "orphan" for o in client.get(PATH).json()["unlinkedPartners"])
    result = post(
        client, headers, PATH, {**body(), "organization_id": "orphan"}, 201
    ).json()
    assert result["organizationId"] == "orphan"
    assert all(o["id"] != "orphan" for o in client.get(PATH).json()["unlinkedPartners"])


def test_deleted_flag_prevents_auth_even_if_active_is_inconsistent(client):
    from app.core.commands import utcnow

    login(client, "shipper")
    with database() as db:
        user = db.get(User, "shipper")
        user.deleted_at = utcnow()
        user.active = True
        db.commit()
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "shipper", "password": "test-password"},
        ).status_code
        == 401
    )

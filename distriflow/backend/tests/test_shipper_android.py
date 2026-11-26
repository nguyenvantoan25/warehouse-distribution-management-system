from sqlalchemy import select, func
from tests.test_access import client
from app.main import app
from app.core.database import get_db
from app.modules.auth.models import AccessSession


def test_android_login_rejects_admin_without_creating_session(client):
    response = client.post(
        "/api/v1/auth/shipper-login",
        json={"username": "admin", "password": "test-password"},
    )
    assert response.status_code == 403
    generator = app.dependency_overrides[get_db]()
    with next(generator) as db:
        assert db.scalar(select(func.count()).select_from(AccessSession)) == 0
    generator.close()


def test_android_shipper_login_cookie_csrf_and_own_scope(client):
    response = client.post(
        "/api/v1/auth/shipper-login",
        json={"username": "shipper", "password": "test-password"},
    )
    assert response.status_code == 200
    profile = response.json()
    assert profile["role"] == "SHIPPER"
    tasks = client.get("/api/v1/pickup-tasks").json()
    assert [t["id"] for t in tasks] == ["assigned"]
    assert client.get("/api/v1/pickup-tasks/foreign").status_code == 404
    assert (
        client.post(
            "/api/v1/pickup-tasks/assigned/respond",
            json={"version": 1, "accepted": True},
        ).status_code
        == 403
    )


def test_android_login_does_not_accept_wrong_password(client):
    response = client.post(
        "/api/v1/auth/shipper-login", json={"username": "shipper", "password": "wrong"}
    )
    assert response.status_code == 401

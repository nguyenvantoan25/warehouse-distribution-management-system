import hashlib
import secrets

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from .models import AccessSession, User
from app.core.commands import utcnow

ROLE_ACCESS = {
    "WAREHOUSE_ADMIN": {
        "dashboard.read",
        "tasks.read",
        "handover.confirm",
        "dispatch.assign",
        "catalog.read",
        "catalog.manage",
        "inbound.read",
        "inbound.create",
        "inbound.manage",
        "outbound.read",
        "outbound.create",
        "outbound.manage",
        "outbound.cancel",
        "inventory.read",
        "inventory.manage",
        "shippers.read",
        "audit.read",
        "accounts.manage",
    },
    "DISPATCH_MANAGER": {"dashboard.read", "tasks.read", "dispatch.assign"},
    "SHIPPER": {
        "tasks.read.own",
        "tasks.respond",
        "tasks.arrive",
        "packages.scan",
        "handover.receive",
    },
    "RETAILER_OWNER": {
        "catalog.read",
        "outbound.read",
        "outbound.create",
        "outbound.cancel",
        "inventory.read",
        "shippers.read",
    },
    "SUPPLIER": {"catalog.read", "inbound.read", "inbound.create"},
}
COOKIE_NAME = "distriflow_session"


def password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1
    ).hex()
    return f"{salt}:{digest}"


def verify_password(password: str, hashed: str) -> bool:
    salt, digest = hashed.split(":")
    actual = hashlib.scrypt(
        password.encode(), salt=salt.encode(), n=16384, r=8, p=1
    ).hex()
    return secrets.compare_digest(actual, digest)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session = db.get(AccessSession, token_hash(request.cookies.get(COOKIE_NAME, "")))
    if not session or session.expires_at <= utcnow():
        raise HTTPException(401, "Phiên đăng nhập đã hết hạn hoặc chưa đăng nhập")
    user = db.get(User, session.user_id)
    if not user or not user.active or user.deleted_at is not None:
        raise HTTPException(401, "Tài khoản không còn hoạt động")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        if not secrets.compare_digest(
            request.headers.get("X-CSRF-Token", ""), session.csrf_token
        ):
            raise HTTPException(403, "CSRF token không hợp lệ")
    request.state.access_session = session
    return user


def require_access(*permissions: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if not ROLE_ACCESS.get(user.role, set()).intersection(permissions):
            raise HTTPException(403, "Bạn không có quyền thực hiện thao tác này")
        return user

    return dependency

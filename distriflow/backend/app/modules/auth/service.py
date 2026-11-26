"""Session creation and public profile; passwords never enter API DTOs."""

import secrets
from datetime import timedelta
from sqlalchemy import select
from fastapi import HTTPException
from app.core.commands import utcnow
from .models import User, AccessSession
from .access import ROLE_ACCESS, token_hash, verify_password


def profile(user: User, session: AccessSession):
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "access": sorted(ROLE_ACCESS.get(user.role, set())),
        "csrfToken": session.csrf_token,
    }


def open_session(db, command, required_role=None):
    user = db.scalar(select(User).where(User.username == command.username))
    if (
        not user
        or not user.active
        or user.deleted_at is not None
        or not verify_password(command.password, user.password_hash)
    ):
        raise HTTPException(401, "Tên đăng nhập hoặc mật khẩu không đúng")
    if required_role and user.role != required_role:
        raise HTTPException(403, "Ứng dụng này chỉ dành cho tài khoản shipper")
    token = secrets.token_urlsafe(48)
    session = AccessSession(
        token_hash=token_hash(token),
        user_id=user.id,
        csrf_token=secrets.token_urlsafe(32),
        expires_at=utcnow() + timedelta(hours=8),
    )
    db.add(session)
    db.commit()
    return user, session, token

"""Explicit account-to-warehouse/organization assignments. No password fields."""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.commands import execute
from app.modules.catalog.models import Organization, PartnerMembership
from app.modules.catalog.service import warehouse
from .access import require_access
from .models import User, AccessSession
from .schemas import ScopeCommand

router = APIRouter(prefix="/accounts", tags=["account-scopes"])


def dto(db, user):
    organization_ids = db.scalars(
        select(PartnerMembership.organization_id).where(
            PartnerMembership.user_id == user.id
        )
    ).all()
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "warehouseName": user.warehouse_scope,
        "organizationIds": list(organization_ids),
        "active": user.active,
    }


@router.get("")
def accounts(
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    users = db.scalars(
        select(User)
        .where(
            or_(
                User.warehouse_scope == actor.warehouse_scope,
                User.warehouse_scope == "",
            )
        )
        .order_by(User.username)
    ).all()
    return [dto(db, user) for user in users]


@router.post("/{user_id}/scope")
def scope(
    user_id: str,
    cmd: ScopeCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    user = db.scalar(
        select(User)
        .where(
            User.id == user_id,
            or_(
                User.warehouse_scope == actor.warehouse_scope,
                User.warehouse_scope == "",
            ),
        )
        .with_for_update()
    )
    if not user:
        raise HTTPException(404, "Tài khoản không thuộc phạm vi quản lý")
    before = dto(db, user)

    def apply():
        selected = warehouse(db, actor, cmd.warehouse_id)
        expected = {"SUPPLIER": "SUPPLIER", "RETAILER_OWNER": "RETAILER"}.get(user.role)
        if expected:
            organization = (
                db.get(Organization, cmd.organization_id)
                if cmd.organization_id
                else None
            )
            if (
                not organization
                or not organization.active
                or organization.kind != expected
            ):
                raise HTTPException(
                    422, "Cần chọn đúng tổ chức đang hoạt động cho vai trò đối tác"
                )
        elif cmd.organization_id:
            raise HTTPException(422, "Vai trò này không gán tổ chức đối tác")
        db.execute(
            delete(PartnerMembership).where(PartnerMembership.user_id == user.id)
        )
        if expected:
            db.add(
                PartnerMembership(user_id=user.id, organization_id=cmd.organization_id)
            )
        user.warehouse_scope = selected.name
        if user.id != actor.id:
            db.execute(delete(AccessSession).where(AccessSession.user_id == user.id))
        db.flush()
        return dto(db, user)

    return execute(
        db, actor.id, key, "account.scope", user.id, cmd.model_dump(), before, apply
    )

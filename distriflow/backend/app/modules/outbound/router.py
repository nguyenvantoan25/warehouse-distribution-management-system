from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.commands import execute
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from app.core.schemas import VersionedCommand
from .schemas import OutboundCreate, PackCommand
from . import service

router = APIRouter(prefix="/outbound-requests", tags=["outbound"])


@router.get("")
def requests(
    db: Session = Depends(get_db), user: User = Depends(require_access("outbound.read"))
):
    return [
        service.dto(db, request)
        for request in db.scalars(service.scoped(db, user)).all()
    ]


@router.post("", status_code=201)
def create(
    cmd: OutboundCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("outbound.create")),
):
    return execute(
        db,
        user.id,
        key,
        "outbound.create",
        "outbounds",
        cmd.model_dump(),
        {},
        lambda: service.create(db, user, cmd),
    )


def run(db, user, request_id, key, action, cmd, operation):
    request = service.get_request(db, user, request_id)
    before = service.dto(db, request)

    def apply():
        operation(db, request, cmd)
        db.flush()
        return service.dto(db, request)

    return execute(
        db, user.id, key, action, request.id, cmd.model_dump(), before, apply
    )


@router.post("/{request_id}/approve")
def approve(
    request_id: str,
    cmd: VersionedCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("outbound.manage")),
):
    return run(db, user, request_id, key, "outbound.approve", cmd, service.approve)


@router.post("/{request_id}/pick")
def pick(
    request_id: str,
    cmd: VersionedCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("outbound.manage")),
):
    return run(db, user, request_id, key, "outbound.pick", cmd, service.pick)


@router.post("/{request_id}/pack")
def pack(
    request_id: str,
    cmd: PackCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("outbound.manage")),
):
    return run(db, user, request_id, key, "outbound.pack", cmd, service.pack)


@router.post("/{request_id}/cancel")
def cancel(
    request_id: str,
    cmd: VersionedCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("outbound.cancel")),
):
    return run(db, user, request_id, key, "outbound.cancel", cmd, service.cancel)

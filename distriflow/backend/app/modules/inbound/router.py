from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.commands import execute
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from . import service
from .schemas import InboundCreate, ReviewCommand, ReceiveCommand, PutawayCommand

router = APIRouter(prefix="/inbound-requests", tags=["inbound"])


@router.get("")
def requests(
    db: Session = Depends(get_db), user: User = Depends(require_access("inbound.read"))
):
    return [
        service.dto(db, request)
        for request in db.scalars(service.scoped(db, user)).all()
    ]


@router.post("", status_code=201)
def create(
    cmd: InboundCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inbound.create")),
):
    return execute(
        db,
        user.id,
        key,
        "inbound.create",
        "inbounds",
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


@router.post("/{request_id}/review")
def review(
    request_id: str,
    cmd: ReviewCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inbound.manage")),
):
    return run(db, user, request_id, key, "inbound.review", cmd, service.review)


@router.post("/{request_id}/receive")
def receive(
    request_id: str,
    cmd: ReceiveCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inbound.manage")),
):
    return run(db, user, request_id, key, "inbound.receive", cmd, service.receive)


@router.post("/{request_id}/putaway")
def putaway(
    request_id: str,
    cmd: PutawayCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inbound.manage")),
):
    return run(db, user, request_id, key, "inbound.putaway", cmd, service.putaway)

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.commands import execute
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from . import service
from .schemas import CreateAccount, UpdateAccount, DeleteAccount

router = APIRouter(prefix="/directory", tags=["account-partner-directory"])


@router.get("")
def list_directory(
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    return service.listing(db, actor)


@router.post("", status_code=201)
def create_account(
    cmd: CreateAccount,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    payload = service.safe_payload(cmd, key, actor.id)
    return execute(
        db,
        actor.id,
        key,
        "directory.create",
        "directory",
        payload,
        {},
        lambda: service.create(db, actor, cmd),
    )


@router.post("/{user_id}/update")
def update_account(
    user_id: str,
    cmd: UpdateAccount,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    user = service.target(db, actor, user_id)
    payload = service.safe_payload(cmd, key, actor.id)
    return execute(
        db,
        actor.id,
        key,
        "directory.update",
        user.id,
        payload,
        service.profile(db, user),
        lambda: service.update(db, user, cmd),
    )


@router.post("/{user_id}/delete")
def delete_account(
    user_id: str,
    cmd: DeleteAccount,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    actor: User = Depends(require_access("accounts.manage")),
):
    user = service.target(db, actor, user_id)
    return execute(
        db,
        actor.id,
        key,
        "directory.delete",
        user.id,
        cmd.model_dump(),
        service.profile(db, user),
        lambda: service.remove(db, user, cmd),
    )

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.commands import execute
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from .schemas import (
    TaskDto,
    AssignCommand,
    RespondCommand,
    VersionedCommand,
)
from app.modules.dispatch.projections import task_dto
from .models import PickupTask
from . import service
from .commands import run

router = APIRouter(tags=["dispatch"])


@router.get("/shippers")
def shippers(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("dispatch.assign", "shippers.read")),
):
    people = db.scalars(
        select(User).where(
            User.role == "SHIPPER",
            User.active.is_(True),
            User.warehouse_scope == user.warehouse_scope,
        )
    ).all()
    return [{"id": person.id, "name": person.display_name or person.username} for person in people]


@router.get("/pickup-tasks", response_model=list[TaskDto])
def tasks(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("tasks.read", "tasks.read.own")),
):
    query = (
        select(PickupTask).where(PickupTask.shipper_id == user.id)
        if user.role == "SHIPPER"
        else select(PickupTask).where(PickupTask.warehouse_name == user.warehouse_scope)
    )
    return [task_dto(db, task) for task in db.scalars(query).all()]


@router.get("/pickup-tasks/{task_id}", response_model=TaskDto)
def detail(
    task_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_access("tasks.read", "tasks.read.own")),
):
    return task_dto(db, service.scoped_task(db, user, task_id))


@router.post("/pickup-tasks/{task_id}/assign", response_model=TaskDto)
def assign(
    task_id: str,
    cmd: AssignCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("dispatch.assign")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "assign",
        cmd,
        lambda task: service.assign(db, user, task, cmd),
    )


@router.post("/pickup-tasks/{task_id}/respond", response_model=TaskDto)
def respond(
    task_id: str,
    cmd: RespondCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("tasks.respond")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "respond",
        cmd,
        lambda task: service.respond(task, cmd),
        own=True,
    )


@router.post("/pickup-tasks/{task_id}/arrive", response_model=TaskDto)
def arrive(
    task_id: str,
    cmd: VersionedCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("tasks.arrive")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "arrive",
        cmd,
        lambda task: service.arrive(task, cmd),
        own=True,
    )

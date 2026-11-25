from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from app.modules.dispatch.commands import run
from app.modules.dispatch.service import scoped_task
from app.modules.dispatch.models import Package
from app.modules.inventory.models import InventoryPosting, InventoryBalance
from .models import Receipt, HandoverConfirmation
from .schemas import ScanCommand
from app.core.schemas import VersionedCommand
from app.modules.dispatch.schemas import TaskDto
from . import service

router = APIRouter(tags=["handover"])


@router.post("/pickup-tasks/{task_id}/scan", response_model=TaskDto)
def scan(
    task_id: str,
    cmd: ScanCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("packages.scan")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "scan",
        cmd,
        lambda task: service.scan(db, task, cmd),
        own=True,
    )


@router.post("/pickup-tasks/{task_id}/shipper-confirm", response_model=TaskDto)
def shipper_confirm(
    task_id: str,
    cmd: VersionedCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("handover.receive")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "shipper-confirm",
        cmd,
        lambda task: service.shipper_confirm(db, user, task, cmd),
        own=True,
    )


@router.post("/pickup-tasks/{task_id}/warehouse-confirm", response_model=TaskDto)
def warehouse_confirm(
    task_id: str,
    cmd: VersionedCommand,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("handover.confirm")),
):
    return run(
        db,
        user,
        task_id,
        idempotency_key,
        "warehouse-confirm",
        cmd,
        lambda task: service.warehouse_confirm(db, user, task, cmd),
    )


@router.get("/pickup-tasks/{task_id}/receipt")
def receipt(
    task_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_access("tasks.read", "tasks.read.own")),
):
    task = scoped_task(db, user, task_id)
    document = db.scalar(select(Receipt).where(Receipt.task_id == task.id))
    if not document:
        raise HTTPException(409, "Chưa phát hành biên nhận")
    confirmations = db.scalars(
        select(HandoverConfirmation).where(HandoverConfirmation.task_id == task.id)
    ).all()
    rows = db.execute(
        select(InventoryPosting, InventoryBalance)
        .join(InventoryBalance, InventoryBalance.id == InventoryPosting.balance_id)
        .where(InventoryPosting.task_id == task.id)
    ).all()
    return {
        "id": document.id,
        "number": document.number,
        "taskCode": task.code,
        "warehouse": task.warehouse_name,
        "issuedAt": document.issued_at.isoformat() + "Z",
        "packages": db.scalars(
            select(Package.code).where(Package.task_id == task.id)
        ).all(),
        "confirmations": [
            {
                "side": c.side,
                "actorId": c.actor_id,
                "version": c.version,
                "at": c.at.isoformat() + "Z",
            }
            for c in confirmations
        ],
        "stockIssues": [
            {"skuCode": b.sku_code, "ownerId": b.owner_id, "quantity": p.quantity}
            for p, b in rows
        ],
    }

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, or_
from app.core.commands import AuditLog
from app.core.commands import utcnow
from app.modules.dispatch.models import PickupTask, Package
from app.modules.handover.models import Receipt
from app.modules.dispatch.projections import task_dto
from app.modules.inbound.models import InboundRequest
from app.modules.outbound.models import OutboundRequest
from app.modules.inventory.models import Warehouse


def dashboard(db, user):
    tasks = db.scalars(
        select(PickupTask).where(PickupTask.warehouse_name == user.warehouse_scope)
    ).all()
    today = datetime.now(timezone(timedelta(hours=7))).date()
    days = {today - timedelta(days=offset): 0 for offset in range(29, -1, -1)}
    counts = dict(
        db.execute(
            select(Package.task_id, func.count(Package.id))
            .where(Package.task_id.in_([task.id for task in tasks]))
            .group_by(Package.task_id)
        ).all()
    )
    for receipt in db.scalars(
        select(Receipt).where(Receipt.task_id.in_([task.id for task in tasks]))
    ).all():
        day = (receipt.issued_at + timedelta(hours=7)).date()
        if day in days:
            days[day] += counts.get(receipt.task_id, 0)
    return {
        "dataSource": {
            "storage": db.get_bind().dialect.name,
            "generatedAt": utcnow().isoformat() + "Z",
            "scope": user.warehouse_scope,
        },
        "flow": [
            {"date": day.isoformat(), "quantity": quantity}
            for day, quantity in days.items()
        ],
        "readyHandover": sum(task.status == "ready_for_handover" for task in tasks),
        "tasks": [task_dto(db, task).model_dump() for task in tasks],
    }

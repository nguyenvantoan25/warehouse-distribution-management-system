from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, or_
from app.core.commands import AuditLog
from app.modules.dispatch.models import PickupTask, Package
from app.modules.handover.models import Receipt
from app.modules.inbound.models import InboundRequest
from app.modules.outbound.models import OutboundRequest
from app.modules.inventory.models import Warehouse


def audit(db, user):
    ids = list(
        db.scalars(
            select(PickupTask.id).where(
                PickupTask.warehouse_name == user.warehouse_scope
            )
        ).all()
    )
    for model in [InboundRequest, OutboundRequest]:
        ids += list(
            db.scalars(
                select(model.id)
                .join(Warehouse, Warehouse.id == model.warehouse_id)
                .where(Warehouse.name == user.warehouse_scope)
            ).all()
        )
    logs = db.scalars(
        select(AuditLog)
        .where(or_(AuditLog.object_id.in_(ids), AuditLog.actor_id == user.id))
        .order_by(AuditLog.at.desc())
        .limit(100)
    ).all()
    return [
        {
            "id": log.id,
            "actorId": log.actor_id,
            "action": log.action,
            "objectId": log.object_id,
            "before": log.before,
            "after": log.after,
            "at": log.at.isoformat() + "Z",
        }
        for log in logs
    ]

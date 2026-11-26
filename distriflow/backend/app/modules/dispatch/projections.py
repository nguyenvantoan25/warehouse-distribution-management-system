"""Read projection joining dispatch tasks to scan/receipt state; never mutates."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.handover.models import PackageScan, Receipt
from .models import PickupTask, Package
from .schemas import TaskDto


def task_dto(db: Session, task: PickupTask) -> TaskDto:
    shipper = db.get(User, task.shipper_id)
    packages = db.scalars(select(Package).where(Package.task_id == task.id)).all()
    scanned = {
        x.package_id
        for x in db.scalars(
            select(PackageScan).where(PackageScan.task_id == task.id)
        ).all()
    }
    return TaskDto(
        id=task.id,
        code=task.code,
        warehouseName=task.warehouse_name,
        packages=[x.code for x in packages],
        status=task.status,
        shipperAccepted=task.shipper_accepted,
        arrivedAtWarehouse=task.arrived_at_warehouse,
        scannedCodes=[x.code for x in packages if x.id in scanned],
        version=task.version,
        receiptId=(db.scalar(select(Receipt.id).where(Receipt.task_id == task.id))),
        shipperId=task.shipper_id,
        shipperName=(shipper.display_name or shipper.username) if shipper else "Chưa phân công",
    )

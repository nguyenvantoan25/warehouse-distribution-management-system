from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.dispatch.models import PickupTask, Package
from app.modules.dispatch.service import check_version, ready
from app.modules.inventory.service import issue_reserved_stock
from .models import PackageScan, HandoverConfirmation, Receipt


def scan(db, task, cmd):
    check_version(task, cmd.version)
    ready(task)
    if not task.shipper_accepted or not task.arrived_at_warehouse:
        raise HTTPException(409, "Cần nhận nhiệm vụ và đến kho trước khi quét")
    package = db.scalar(
        select(Package).where(
            Package.task_id == task.id, Package.code == cmd.package_code.strip()
        )
    )
    if not package:
        raise HTTPException(422, "Kiện không thuộc nhiệm vụ bàn giao")
    if db.scalar(
        select(PackageScan).where(
            PackageScan.task_id == task.id, PackageScan.package_id == package.id
        )
    ):
        raise HTTPException(409, "Kiện đã được quét; tiến độ không thay đổi")
    db.add(PackageScan(task_id=task.id, package_id=package.id))
    task.version += 1


def shipper_confirm(db, user, task, cmd):
    check_version(task, cmd.version)
    ready(task)
    packages = db.scalars(select(Package.id).where(Package.task_id == task.id)).all()
    scans = db.scalars(
        select(PackageScan.package_id).where(PackageScan.task_id == task.id)
    ).all()
    if (
        not task.shipper_accepted
        or not task.arrived_at_warehouse
        or not packages
        or set(packages) != set(scans)
    ):
        raise HTTPException(
            409, "Cần đến kho và đối chiếu đầy đủ kiện trước khi xác nhận"
        )
    db.add(
        HandoverConfirmation(
            task_id=task.id, side="shipper", version=task.version, actor_id=user.id
        )
    )
    task.status = "pending_confirmations"
    task.version += 1


def warehouse_confirm(db, user, task, cmd):
    check_version(task, cmd.version)
    if task.status != "pending_confirmations":
        raise HTTPException(409, "Phiếu chưa đủ điều kiện xác nhận kho")
    confirmation = db.scalar(
        select(HandoverConfirmation)
        .where(
            HandoverConfirmation.task_id == task.id,
            HandoverConfirmation.side == "shipper",
            HandoverConfirmation.actor_id == task.shipper_id,
        )
        .order_by(HandoverConfirmation.version.desc())
    )
    if not confirmation:
        raise HTTPException(409, "Chưa có xác nhận hợp lệ của shipper được phân công")
    issue_reserved_stock(db, task.id, task.warehouse_name)
    from app.modules.outbound.models import OutboundTask, OutboundRequest

    link = db.scalar(select(OutboundTask).where(OutboundTask.task_id == task.id))
    if link:
        request = db.get(OutboundRequest, link.request_id)
        request.status = "handed_over"
        request.version += 1
    db.add_all(
        [
            HandoverConfirmation(
                task_id=task.id,
                side="warehouse",
                version=confirmation.version,
                actor_id=user.id,
            ),
            Receipt(task_id=task.id, number=f"BBBG-{task.code}"),
        ]
    )
    task.status = "handed_over"
    task.version += 1

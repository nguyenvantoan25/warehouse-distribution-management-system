from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from .models import PickupTask


def scoped_task(db: Session, user: User, task_id: str, own=False):
    query = select(PickupTask).where(PickupTask.id == task_id)
    query = (
        query.where(PickupTask.shipper_id == user.id)
        if own or user.role == "SHIPPER"
        else query.where(PickupTask.warehouse_name == user.warehouse_scope)
    )
    task = db.scalar(query.with_for_update())
    if not task:
        raise HTTPException(404, "Không tìm thấy nhiệm vụ trong phạm vi của bạn")
    return task


def check_version(task, version):
    if task.version != version:
        raise HTTPException(409, "Phiên đã thay đổi, hãy tải lại")


def ready(task):
    if task.status != "ready_for_handover":
        raise HTTPException(409, "Nhiệm vụ không còn ở bước này")


def assign(db, user, task, cmd):
    check_version(task, cmd.version)
    ready(task)
    from app.modules.outbound.models import OutboundTask, OutboundRequest

    link = db.scalar(select(OutboundTask).where(OutboundTask.task_id == task.id))
    if link:
        request = db.get(OutboundRequest, link.request_id)
        if (
            request.shipper_mode == "OWNER_ASSIGNED"
            and request.shipper_id != cmd.shipper_id
        ):
            raise HTTPException(
                409,
                "Chủ hàng đã chỉ định shipper; không tự thay đổi phương án hoặc người nhận",
            )
    if task.shipper_accepted or task.arrived_at_warehouse:
        raise HTTPException(409, "Shipper đã nhận nhiệm vụ; không thể đổi phân công")
    shipper = db.get(User, cmd.shipper_id)
    if (
        not shipper
        or not shipper.active
        or shipper.role != "SHIPPER"
        or shipper.warehouse_scope != user.warehouse_scope
    ):
        raise HTTPException(422, "Shipper không hoạt động hoặc ngoài phạm vi kho")
    task.shipper_id = shipper.id
    task.version += 1


def respond(task, cmd):
    check_version(task, cmd.version)
    ready(task)
    if task.shipper_accepted:
        raise HTTPException(409, "Nhiệm vụ đã được tiếp nhận")
    if not cmd.accepted:
        raise HTTPException(409, "Cần điều phối lại, không tự đổi phương án vận chuyển")
    task.shipper_accepted = True
    task.version += 1


def arrive(task, cmd):
    check_version(task, cmd.version)
    ready(task)
    if not task.shipper_accepted or task.arrived_at_warehouse:
        raise HTTPException(409, "Cần nhận nhiệm vụ trước hoặc đã ghi nhận đến kho")
    task.arrived_at_warehouse = True
    task.version += 1

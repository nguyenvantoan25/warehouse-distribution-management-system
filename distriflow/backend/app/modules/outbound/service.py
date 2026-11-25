import uuid
from fastapi import HTTPException
from sqlalchemy import select, update
from app.modules.auth.models import User
from app.modules.catalog.models import Organization, Sku
from app.modules.catalog.service import (
    owner_scope,
    warehouse,
    validate_lines,
    memberships,
)
from app.modules.dispatch.models import PickupTask, Package
from app.modules.inventory.models import Warehouse, InventoryBalance, StockReservation
from .models import (
    OutboundRequest,
    OutboundLine,
    OutboundAllocation,
    OutboundTask,
    PackageItem,
)


def scoped(db, user):
    query = (
        select(OutboundRequest)
        .join(Warehouse, Warehouse.id == OutboundRequest.warehouse_id)
        .where(Warehouse.name == user.warehouse_scope)
    )
    if user.role == "RETAILER_OWNER":
        query = query.where(OutboundRequest.owner_id.in_(memberships(db, user)))
    return query


def get_request(db, user, request_id):
    result = db.scalar(
        scoped(db, user).where(OutboundRequest.id == request_id).with_for_update()
    )
    if not result:
        raise HTTPException(404, "Không tìm thấy yêu cầu xuất trong phạm vi của bạn")
    return result


def dto(db, request):
    owner = db.get(Organization, request.owner_id)
    link = db.get(OutboundTask, request.id)
    lines = db.scalars(
        select(OutboundLine).where(OutboundLine.request_id == request.id)
    ).all()
    return {
        "id": request.id,
        "code": request.code,
        "ownerId": request.owner_id,
        "ownerName": owner.name,
        "warehouseId": request.warehouse_id,
        "warehouseName": db.get(Warehouse, request.warehouse_id).name,
        "status": request.status,
        "version": request.version,
        "shipperMode": request.shipper_mode,
        "shipperId": request.shipper_id,
        "taskId": link.task_id if link else None,
        "createdAt": request.created_at.isoformat() + "Z",
        "lines": [
            {
                "id": line.id,
                "skuId": line.sku_id,
                "skuCode": db.get(Sku, line.sku_id).code,
                "skuName": db.get(Sku, line.sku_id).name,
                "unit": db.get(Sku, line.sku_id).base_unit,
                "quantity": line.quantity,
            }
            for line in lines
        ],
    }


def create(db, user, cmd):
    owner_scope(db, user, cmd.owner_id)
    warehouse(db, user, cmd.warehouse_id)
    validate_lines(db, cmd.owner_id, cmd.lines)
    if cmd.shipper_mode == "OWNER_ASSIGNED":
        shipper = db.get(User, cmd.shipper_id)
        if (
            not shipper
            or not shipper.active
            or shipper.role != "SHIPPER"
            or shipper.warehouse_scope != user.warehouse_scope
        ):
            raise HTTPException(422, "Shipper chỉ định không hợp lệ")
    elif cmd.shipper_id:
        raise HTTPException(422, "Phương án DistriFlow sẽ do điều phối gán shipper")
    request = OutboundRequest(
        code="XK-" + uuid.uuid4().hex[:12].upper(),
        owner_id=cmd.owner_id,
        warehouse_id=cmd.warehouse_id,
        shipper_mode=cmd.shipper_mode,
        shipper_id=cmd.shipper_id,
    )
    db.add(request)
    db.flush()
    db.add_all(
        [
            OutboundLine(
                request_id=request.id, sku_id=line.sku_id, quantity=line.quantity
            )
            for line in cmd.lines
        ]
    )
    db.flush()
    return dto(db, request)


def state(request, cmd, expected):
    if request.version != cmd.version or request.status not in expected:
        raise HTTPException(409, "Yêu cầu xuất đã thay đổi hoặc sai bước xử lý")


def approve(db, request, cmd):
    state(request, cmd, {"submitted"})
    for line in db.scalars(
        select(OutboundLine)
        .where(OutboundLine.request_id == request.id)
        .order_by(OutboundLine.sku_id)
    ).all():
        sku = db.get(Sku, line.sku_id)
        balances = db.scalars(
            select(InventoryBalance)
            .where(
                InventoryBalance.owner_id == request.owner_id,
                InventoryBalance.sku_code == sku.code,
                InventoryBalance.warehouse_id == request.warehouse_id,
            )
            .order_by(InventoryBalance.id)
            .with_for_update()
        ).all()
        remaining = line.quantity
        for balance in balances:
            quantity = min(
                remaining, balance.on_hand - balance.reserved - balance.unavailable
            )
            if quantity <= 0:
                continue
            result = db.execute(
                update(InventoryBalance)
                .where(
                    InventoryBalance.id == balance.id,
                    InventoryBalance.on_hand
                    - InventoryBalance.reserved
                    - InventoryBalance.unavailable
                    >= quantity,
                )
                .values(reserved=InventoryBalance.reserved + quantity)
            )
            if result.rowcount != 1:
                raise HTTPException(409, "Tồn kho vừa thay đổi; vui lòng duyệt lại")
            db.add(
                OutboundAllocation(
                    line_id=line.id, balance_id=balance.id, quantity=quantity
                )
            )
            remaining -= quantity
            if remaining == 0:
                break
        if remaining:
            raise HTTPException(
                409, f"SKU {sku.code} không đủ khả dụng; chưa giữ hàng cho yêu cầu này"
            )
    request.status = "approved"
    request.version += 1


def pick(db, request, cmd):
    state(request, cmd, {"approved"})
    request.status = "picked"
    request.version += 1


def pack(db, request, cmd):
    state(request, cmd, {"picked"})
    lines = db.scalars(
        select(OutboundLine).where(OutboundLine.request_id == request.id)
    ).all()
    task = PickupTask(
        code="BG-" + request.code[3:],
        warehouse_name=db.get(Warehouse, request.warehouse_id).name,
        shipper_id=request.shipper_id,
    )
    db.add(task)
    db.flush()
    db.add(OutboundTask(request_id=request.id, task_id=task.id))
    packages = [
        Package(task_id=task.id, code=f"{task.code}-K{i+1:03}")
        for i in range(cmd.package_count)
    ]
    db.add_all(packages)
    db.flush()
    cursor = 0
    occupied = set()
    totals = {}
    for line in lines:
        for i, package in enumerate(packages):
            quantity = line.quantity // cmd.package_count + int(
                (i - cursor) % cmd.package_count < line.quantity % cmd.package_count
            )
            if quantity:
                occupied.add(package.id)
                db.add(
                    PackageItem(
                        package_id=package.id, line_id=line.id, quantity=quantity
                    )
                )
        cursor = (cursor + line.quantity) % cmd.package_count
        for allocation in db.scalars(
            select(OutboundAllocation).where(
                OutboundAllocation.line_id == line.id,
                OutboundAllocation.state == "reserved",
            )
        ).all():
            totals[allocation.balance_id] = (
                totals.get(allocation.balance_id, 0) + allocation.quantity
            )
    if len(occupied) != len(packages):
        raise HTTPException(
            422, "Không đủ hàng để tạo số kiện đã chọn; không tạo kiện rỗng"
        )
    if not totals:
        raise HTTPException(409, "Không có lượng giữ hợp lệ để đóng kiện")
    db.add_all(
        [
            StockReservation(task_id=task.id, balance_id=balance_id, quantity=quantity)
            for balance_id, quantity in totals.items()
        ]
    )
    request.status = "packed"
    request.version += 1


def cancel(db, request, cmd):
    state(request, cmd, {"submitted", "approved"})
    if request.status == "approved":
        allocations = db.scalars(
            select(OutboundAllocation)
            .join(OutboundLine, OutboundLine.id == OutboundAllocation.line_id)
            .where(
                OutboundLine.request_id == request.id,
                OutboundAllocation.state == "reserved",
            )
            .order_by(OutboundAllocation.balance_id)
            .with_for_update()
        ).all()
        for allocation in allocations:
            result = db.execute(
                update(InventoryBalance)
                .where(
                    InventoryBalance.id == allocation.balance_id,
                    InventoryBalance.reserved >= allocation.quantity,
                )
                .values(reserved=InventoryBalance.reserved - allocation.quantity)
            )
            if result.rowcount != 1:
                raise HTTPException(409, "Lượng giữ không hợp lệ; không thể hủy")
            allocation.state = "released"
    request.status = "cancelled"
    request.version += 1

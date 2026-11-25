import uuid
from fastapi import HTTPException
from sqlalchemy import select, update
from app.modules.catalog.models import Sku, Organization, StorageLocation
from app.modules.catalog.service import (
    warehouse,
    supplier_scope,
    validate_lines,
    memberships,
)
from app.modules.inventory.models import (
    InventoryBalance,
    Warehouse,
    BalanceLocation,
    InboundPosting,
)
from .models import InboundRequest, InboundLine


def scoped(db, user):
    query = (
        select(InboundRequest)
        .join(Warehouse, Warehouse.id == InboundRequest.warehouse_id)
        .where(Warehouse.name == user.warehouse_scope)
    )
    if user.role == "SUPPLIER":
        query = query.where(InboundRequest.supplier_id.in_(memberships(db, user)))
    elif user.role == "RETAILER_OWNER":
        query = query.where(InboundRequest.owner_id.in_(memberships(db, user)))
    return query


def get_request(db, user, request_id):
    result = db.scalar(
        scoped(db, user).where(InboundRequest.id == request_id).with_for_update()
    )
    if not result:
        raise HTTPException(404, "Không tìm thấy yêu cầu nhập trong phạm vi của bạn")
    return result


def dto(db, request):
    owner = db.get(Organization, request.owner_id)
    supplier = db.get(Organization, request.supplier_id)
    lines = db.scalars(
        select(InboundLine).where(InboundLine.request_id == request.id)
    ).all()
    return {
        "id": request.id,
        "code": request.code,
        "ownerId": request.owner_id,
        "ownerName": owner.name,
        "supplierId": request.supplier_id,
        "supplierName": supplier.name,
        "warehouseId": request.warehouse_id,
        "warehouseName": db.get(Warehouse, request.warehouse_id).name,
        "status": request.status,
        "version": request.version,
        "note": request.note,
        "createdAt": request.created_at.isoformat() + "Z",
        "lines": [
            {
                "id": line.id,
                "skuId": line.sku_id,
                "skuCode": db.get(Sku, line.sku_id).code,
                "skuName": db.get(Sku, line.sku_id).name,
                "unit": db.get(Sku, line.sku_id).base_unit,
                "quantity": line.quantity,
                "good": line.good,
                "quarantined": line.quarantined,
            }
            for line in lines
        ],
    }


def create(db, user, cmd):
    warehouse(db, user, cmd.warehouse_id)
    validate_lines(db, cmd.owner_id, cmd.lines)
    supplier_scope(
        db, user, cmd.supplier_id, cmd.owner_id, [line.sku_id for line in cmd.lines]
    )
    request = InboundRequest(
        code="NK-" + uuid.uuid4().hex[:12].upper(),
        supplier_id=cmd.supplier_id,
        owner_id=cmd.owner_id,
        warehouse_id=cmd.warehouse_id,
    )
    db.add(request)
    db.flush()
    db.add_all(
        [
            InboundLine(
                request_id=request.id, sku_id=line.sku_id, quantity=line.quantity
            )
            for line in cmd.lines
        ]
    )
    db.flush()
    return dto(db, request)


def state(request, cmd, expected):
    if request.version != cmd.version or request.status != expected:
        raise HTTPException(409, "Yêu cầu nhập đã thay đổi hoặc sai bước xử lý")


def review(db, request, cmd):
    state(request, cmd, "submitted")
    if not cmd.accepted and not cmd.note.strip():
        raise HTTPException(422, "Cần lý do từ chối")
    request.status = "approved" if cmd.accepted else "rejected"
    request.note = cmd.note
    request.version += 1


def receive(db, request, cmd):
    state(request, cmd, "approved")
    lines = db.scalars(
        select(InboundLine).where(InboundLine.request_id == request.id)
    ).all()
    submitted = {line.line_id: line for line in cmd.lines}
    if len(submitted) != len(cmd.lines) or set(submitted) != {
        line.id for line in lines
    }:
        raise HTTPException(422, "Phải kiểm nhận đủ các dòng hàng, không trùng dòng")
    for line in lines:
        received = submitted[line.id]
        if received.good + received.quarantined > line.quantity:
            raise HTTPException(422, "Tổng lượng kiểm nhận không được vượt kế hoạch")
        if (
            received.good != line.quantity or received.quarantined
        ) and not cmd.note.strip():
            raise HTTPException(422, "Cần ghi lý do thiếu hoặc hàng cách ly")
        line.good = received.good
        line.quarantined = received.quarantined
    request.status = "received"
    request.note = cmd.note
    request.version += 1


def putaway(db, request, cmd):
    state(request, cmd, "received")
    location = db.get(StorageLocation, cmd.location_id)
    if not location or location.warehouse_id != request.warehouse_id:
        raise HTTPException(422, "Vị trí không thuộc kho kiểm nhận")
    for line in db.scalars(
        select(InboundLine).where(InboundLine.request_id == request.id)
    ).all():
        if line.good + line.quarantined == 0:
            continue
        sku = db.get(Sku, line.sku_id)
        balance = db.scalar(
            select(InventoryBalance)
            .join(BalanceLocation, BalanceLocation.balance_id == InventoryBalance.id)
            .where(
                InventoryBalance.owner_id == request.owner_id,
                InventoryBalance.sku_code == sku.code,
                InventoryBalance.warehouse_id == request.warehouse_id,
                BalanceLocation.location_id == location.id,
            )
            .with_for_update()
        )
        if not balance:
            balance = InventoryBalance(
                owner_id=request.owner_id,
                sku_code=sku.code,
                warehouse_id=request.warehouse_id,
                on_hand=0,
                reserved=0,
                unavailable=0,
            )
            db.add(balance)
            db.flush()
            db.add(BalanceLocation(balance_id=balance.id, location_id=location.id))
        db.execute(
            update(InventoryBalance)
            .where(InventoryBalance.id == balance.id)
            .values(
                on_hand=InventoryBalance.on_hand + line.good + line.quarantined,
                unavailable=InventoryBalance.unavailable + line.quarantined,
            )
        )
        db.add(
            InboundPosting(
                line_id=line.id,
                balance_id=balance.id,
                quantity=line.good + line.quarantined,
                quarantined=line.quarantined,
            )
        )
    request.status = "stocked"
    request.version += 1

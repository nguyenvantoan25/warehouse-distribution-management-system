"""Logical rack coordinates and recorded inventory, not a surveyed physical floor plan."""

from fastapi import HTTPException
from sqlalchemy import select
from app.modules.catalog.models import Organization, Sku, StorageLocation
from .models import BalanceLocation, InventoryBalance, Warehouse

LAYOUT = {
    "rows": 8,
    "levels": 10,
    "columns": 10,
    "rackType": "single",
    "totalPositions": 800,
}


def coordinates():
    for row in range(1, 9):
        for level in range(1, 11):
            for column in range(1, 11):
                yield row, level, column


def location_code(row, level, column):
    return f"H{row:02d}-T{level:02d}-C{column:02d}"


def scoped_warehouse(db, user, warehouse_id=None, lock=False):
    query = select(Warehouse).where(Warehouse.name == user.warehouse_scope)
    if warehouse_id is not None:
        query = query.where(Warehouse.id == warehouse_id)
    if lock:
        query = query.with_for_update()
    result = db.scalar(query)
    if not result:
        raise HTTPException(404, "Chưa có kho hoặc kho không thuộc phạm vi được cấp")
    return result


def initialize_racks(db, user, cmd):
    # Serialize setup for this warehouse; constraints are the final concurrent-write guard.
    warehouse = scoped_warehouse(db, user, cmd.warehouse_id, lock=True)
    existing = db.scalars(
        select(StorageLocation).where(StorageLocation.warehouse_id == warehouse.id)
    ).all()
    mapped = {
        (loc.rack_row, loc.rack_level, loc.rack_bay): loc
        for loc in existing
        if loc.rack_row is not None
    }
    codes = {loc.code for loc in existing}
    missing = [coord for coord in coordinates() if coord not in mapped]
    # Do not attach coordinates to an old code silently, even when the names coincide.
    if any(location_code(*coord) in codes for coord in missing):
        raise HTTPException(
            409, "Mã kệ trùng vị trí hiện có; cần kiểm tra danh mục, không tự ghi đè"
        )
    for row, level, column in missing:
        db.add(
            StorageLocation(
                warehouse_id=warehouse.id,
                code=location_code(row, level, column),
                rack_row=row,
                rack_level=level,
                rack_bay=column,
                rack_depth=1,
            )
        )
    db.flush()
    return {
        "id": warehouse.id,
        "created": len(missing),
        "configured": 800,
        "layout": LAYOUT,
    }


def rack_map(db, user):
    warehouse = db.scalar(
        select(Warehouse).where(Warehouse.name == user.warehouse_scope)
    )
    if warehouse is None:
        return {
            "warehouse": None,
            "layout": LAYOUT,
            "locations": [],
            "otherLocationCount": 0,
            "unmappedBalanceCount": 0,
        }
    locations = db.scalars(
        select(StorageLocation).where(StorageLocation.warehouse_id == warehouse.id)
    ).all()
    mapped = [loc for loc in locations if loc.rack_row is not None]
    lines = {loc.id: [] for loc in mapped}
    stock = db.execute(
        select(InventoryBalance, BalanceLocation.location_id, Sku, Organization)
        .outerjoin(BalanceLocation, BalanceLocation.balance_id == InventoryBalance.id)
        .join(Sku, Sku.code == InventoryBalance.sku_code)
        .join(Organization, Organization.id == InventoryBalance.owner_id)
        .where(
            InventoryBalance.warehouse_id == warehouse.id, InventoryBalance.on_hand > 0
        )
        .order_by(Sku.code, Organization.name, InventoryBalance.id)
    ).all()
    unmapped = 0
    for balance, location_id, sku, owner in stock:
        if location_id not in lines:
            unmapped += 1
            continue
        lines[location_id].append(
            {
                "id": balance.id,
                "skuCode": sku.code,
                "skuName": sku.name,
                "ownerName": owner.name,
                "unit": sku.base_unit,
                "onHand": balance.on_hand,
                "reserved": balance.reserved,
                "unavailable": balance.unavailable,
                "available": balance.on_hand - balance.reserved - balance.unavailable,
            }
        )
    result = []
    for loc in sorted(
        mapped, key=lambda x: (x.rack_row, x.rack_level, x.rack_bay, x.rack_depth)
    ):
        items = lines[loc.id]
        status = (
            "unavailable"
            if any(i["unavailable"] for i in items)
            else (
                "reserved"
                if any(i["reserved"] for i in items)
                else "occupied" if items else "empty"
            )
        )
        result.append(
            {
                "id": loc.id,
                "code": loc.code,
                "row": loc.rack_row,
                "level": loc.rack_level,
                "column": loc.rack_bay,
                "status": status,
                "items": items,
            }
        )
    return {
        "warehouse": {"id": warehouse.id, "name": warehouse.name},
        "layout": LAYOUT,
        "locations": result,
        "otherLocationCount": len(locations) - len(mapped),
        "unmappedBalanceCount": unmapped,
    }

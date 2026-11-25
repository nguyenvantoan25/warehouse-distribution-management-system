from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .models import InventoryBalance, InventoryPosting, StockReservation, Warehouse


def scoped_balances(db: Session, warehouse_name: str):
    return db.scalars(
        select(InventoryBalance)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .where(Warehouse.name == warehouse_name)
    ).all()


def issue_reserved_stock(db: Session, task_id: str, warehouse_name: str):
    """Called inside the handover transaction; never commits independently."""
    reservations = db.scalars(
        select(StockReservation)
        .where(StockReservation.task_id == task_id)
        .order_by(StockReservation.balance_id)
        .with_for_update()
    ).all()
    if not reservations:
        raise HTTPException(
            409, "Phiếu chưa có chi tiết giữ hàng. Cần kiểm tra tồn trước khi bàn giao."
        )
    for reservation in reservations:
        if reservation.state != "reserved":
            raise HTTPException(409, "Lượng giữ đã được ghi xuất hoặc không còn hợp lệ")
        balance = db.scalar(
            select(InventoryBalance)
            .where(InventoryBalance.id == reservation.balance_id)
            .with_for_update()
        )
        warehouse = db.get(Warehouse, balance.warehouse_id) if balance else None
        if not balance or not warehouse or warehouse.name != warehouse_name:
            raise HTTPException(409, "Lượng giữ không thuộc kho bàn giao")
        if (
            balance.reserved < reservation.quantity
            or balance.on_hand - balance.unavailable < reservation.quantity
        ):
            raise HTTPException(
                409, "Tồn kho hoặc lượng giữ không đủ; không ghi xuất một phần"
            )
        result = db.execute(
            update(InventoryBalance)
            .where(
                InventoryBalance.id == balance.id,
                InventoryBalance.reserved >= reservation.quantity,
                InventoryBalance.on_hand - InventoryBalance.unavailable
                >= reservation.quantity,
            )
            .values(
                on_hand=InventoryBalance.on_hand - reservation.quantity,
                reserved=InventoryBalance.reserved - reservation.quantity,
            )
        )
        if result.rowcount != 1:
            raise HTTPException(409, "Tồn vừa thay đổi, không thể ghi xuất")
        reservation.state = "issued"
        db.add(
            InventoryPosting(
                reservation_id=reservation.id,
                balance_id=balance.id,
                task_id=task_id,
                quantity=reservation.quantity,
            )
        )


def balance_dto(balance):
    return {
        "id": balance.id,
        "ownerId": balance.owner_id,
        "skuCode": balance.sku_code,
        "warehouseId": balance.warehouse_id,
        "onHand": balance.on_hand,
        "reserved": balance.reserved,
        "unavailable": balance.unavailable,
        "available": balance.on_hand - balance.reserved - balance.unavailable,
    }


def hold_stock(db, user, cmd):
    balance = db.scalar(
        select(InventoryBalance)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .where(
            InventoryBalance.id == cmd.balance_id,
            Warehouse.name == user.warehouse_scope,
        )
        .with_for_update()
    )
    if not balance:
        raise HTTPException(404, "Không tìm thấy dòng tồn trong phạm vi kho")
    before = balance_dto(balance)

    def apply():
        condition = (
            InventoryBalance.unavailable >= cmd.quantity
            if cmd.release
            else InventoryBalance.on_hand
            - InventoryBalance.reserved
            - InventoryBalance.unavailable
            >= cmd.quantity
        )
        result = db.execute(
            update(InventoryBalance)
            .where(InventoryBalance.id == balance.id, condition)
            .values(
                unavailable=InventoryBalance.unavailable
                + (-cmd.quantity if cmd.release else cmd.quantity)
            )
        )
        if result.rowcount != 1:
            raise HTTPException(
                409, "Không đủ lượng phù hợp; không thể khóa chồng lên hàng đã giữ"
            )
        db.refresh(balance)
        return balance_dto(balance)

    return balance, before, apply

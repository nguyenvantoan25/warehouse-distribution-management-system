import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.commands import utcnow


def uid() -> str:
    return str(uuid.uuid4())


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        CheckConstraint(
            "on_hand >= reserved + unavailable AND reserved >= 0 AND unavailable >= 0",
            name="ck_stock_nonnegative",
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    owner_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    sku_code: Mapped[str] = mapped_column(ForeignKey("skus.code"))
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    unavailable: Mapped[int] = mapped_column(Integer, default=0)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        UniqueConstraint("source_task_id", "kind", name="uq_stock_issue_per_task"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    source_task_id: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class StockReservation(Base):
    __tablename__ = "stock_reservations"
    __table_args__ = (
        UniqueConstraint("task_id", "balance_id"),
        CheckConstraint("quantity > 0", name="ck_reservation_positive"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"), index=True)
    balance_id: Mapped[str] = mapped_column(ForeignKey("inventory_balances.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String, default="reserved")


class InventoryPosting(Base):
    __tablename__ = "inventory_postings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    reservation_id: Mapped[str] = mapped_column(
        ForeignKey("stock_reservations.id"), unique=True
    )
    balance_id: Mapped[str] = mapped_column(
        ForeignKey("inventory_balances.id"), index=True
    )
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String, default="HANDOVER_ISSUE")
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class BalanceLocation(Base):
    __tablename__ = "balance_locations"
    balance_id: Mapped[str] = mapped_column(
        ForeignKey("inventory_balances.id"), primary_key=True
    )
    location_id: Mapped[str] = mapped_column(ForeignKey("storage_locations.id"))


class InboundPosting(Base):
    __tablename__ = "inbound_postings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    line_id: Mapped[str] = mapped_column(ForeignKey("inbound_lines.id"), unique=True)
    balance_id: Mapped[str] = mapped_column(ForeignKey("inventory_balances.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    quarantined: Mapped[int] = mapped_column(Integer)
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

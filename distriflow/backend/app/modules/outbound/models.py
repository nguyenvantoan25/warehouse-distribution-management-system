import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.core.commands import utcnow


def uid():
    return str(uuid.uuid4())


class OutboundRequest(Base):
    __tablename__ = "outbound_requests"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String, unique=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    shipper_mode: Mapped[str] = mapped_column(String)
    shipper_id: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="submitted")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __mapper_args__ = {"version_id_col": version, "version_id_generator": False}


class OutboundLine(Base):
    __tablename__ = "outbound_lines"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("outbound_requests.id"), index=True
    )
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"))
    quantity: Mapped[int] = mapped_column(Integer)


class OutboundAllocation(Base):
    __tablename__ = "outbound_allocations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    line_id: Mapped[str] = mapped_column(ForeignKey("outbound_lines.id"), index=True)
    balance_id: Mapped[str] = mapped_column(ForeignKey("inventory_balances.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String, default="reserved")


class OutboundTask(Base):
    __tablename__ = "outbound_tasks"
    request_id: Mapped[str] = mapped_column(
        ForeignKey("outbound_requests.id"), primary_key=True
    )
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"), unique=True)


class PackageItem(Base):
    __tablename__ = "package_items"
    __table_args__ = (UniqueConstraint("package_id", "line_id"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    package_id: Mapped[str] = mapped_column(ForeignKey("packages.id"), index=True)
    line_id: Mapped[str] = mapped_column(ForeignKey("outbound_lines.id"))
    quantity: Mapped[int] = mapped_column(Integer)

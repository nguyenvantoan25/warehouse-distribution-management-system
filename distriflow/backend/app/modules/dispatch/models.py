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


class PickupTask(Base):
    __tablename__ = "pickup_tasks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String, unique=True)
    warehouse_name: Mapped[str] = mapped_column(String)
    shipper_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="ready_for_handover")
    version: Mapped[int] = mapped_column(Integer, default=1)
    __mapper_args__ = {"version_id_col": version, "version_id_generator": False}
    shipper_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    arrived_at_warehouse: Mapped[bool] = mapped_column(Boolean, default=False)


class Package(Base):
    __tablename__ = "packages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"), index=True)
    code: Mapped[str] = mapped_column(String, unique=True)

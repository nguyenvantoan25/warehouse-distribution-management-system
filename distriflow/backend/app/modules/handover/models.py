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


class PackageScan(Base):
    __tablename__ = "package_scans"
    __table_args__ = (
        UniqueConstraint("task_id", "package_id", name="uq_task_package_scan"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"))
    package_id: Mapped[str] = mapped_column(ForeignKey("packages.id"))
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HandoverConfirmation(Base):
    __tablename__ = "handover_confirmations"
    __table_args__ = (
        UniqueConstraint("task_id", "side", "version", name="uq_confirmation_version"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"))
    side: Mapped[str] = mapped_column(String)
    version: Mapped[int] = mapped_column(Integer)
    actor_id: Mapped[str] = mapped_column(String)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Receipt(Base):
    __tablename__ = "handover_receipts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    task_id: Mapped[str] = mapped_column(ForeignKey("pickup_tasks.id"), unique=True)
    number: Mapped[str] = mapped_column(String, unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdempotencyRequest(Base):
    __tablename__ = "idempotency_requests"
    __table_args__ = (UniqueConstraint("actor_id", "key", name="uq_actor_idempotency"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String)
    task_id: Mapped[str] = mapped_column(String)
    response_status: Mapped[str] = mapped_column(String)

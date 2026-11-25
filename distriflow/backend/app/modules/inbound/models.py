import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base
from app.core.commands import utcnow


def uid():
    return str(uuid.uuid4())


class InboundRequest(Base):
    __tablename__ = "inbound_requests"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String, unique=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    status: Mapped[str] = mapped_column(String, default="submitted")
    version: Mapped[int] = mapped_column(Integer, default=1)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    __mapper_args__ = {"version_id_col": version, "version_id_generator": False}


class InboundLine(Base):
    __tablename__ = "inbound_lines"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("inbound_requests.id"), index=True
    )
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    good: Mapped[int] = mapped_column(Integer, default=0)
    quarantined: Mapped[int] = mapped_column(Integer, default=0)

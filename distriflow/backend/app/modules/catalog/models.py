import uuid
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def uid():
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    supplied_goods: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class PartnerMembership(Base):
    __tablename__ = "partner_memberships"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"), primary_key=True
    )


class Sku(Base):
    __tablename__ = "skus"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    base_unit: Mapped[str] = mapped_column(String)
    owner_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)


class SupplyRelationship(Base):
    __tablename__ = "supply_relationships"
    __table_args__ = (UniqueConstraint("supplier_id", "owner_id", "sku_id"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"))


class StorageLocation(Base):
    __tablename__ = "storage_locations"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "code"),
        UniqueConstraint(
            "warehouse_id",
            "rack_row",
            "rack_level",
            "rack_bay",
            "rack_depth",
            name="uq_storage_rack_coordinate",
        ),
        CheckConstraint(
            "(rack_row IS NULL AND rack_level IS NULL AND rack_bay IS NULL AND rack_depth IS NULL) OR "
            "(rack_row IS NOT NULL AND rack_level IS NOT NULL AND rack_bay IS NOT NULL AND rack_depth IS NOT NULL "
            "AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 "
            "AND rack_bay BETWEEN 1 AND 10 AND rack_depth = 1)",
            name="ck_storage_rack_coordinate",
        ),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    code: Mapped[str] = mapped_column(String)
    # Nullable for existing/manual locations; never infer coordinates from a legacy code.
    rack_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rack_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rack_bay: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rack_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)

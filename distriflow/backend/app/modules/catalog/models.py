import uuid
from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
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
    __table_args__ = (UniqueConstraint("warehouse_id", "code"),)
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    code: Mapped[str] = mapped_column(String)

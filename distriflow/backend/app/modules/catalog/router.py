from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.commands import execute
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from app.modules.inventory.models import Warehouse
from .models import Organization, Sku, SupplyRelationship, StorageLocation
from .service import memberships, warehouse, org_dto, sku_dto, create_warehouse
from .schemas import (
    PartnerCreate,
    SkuCreate,
    SupplyCreate,
    LocationCreate,
    WarehouseCreate,
)

router = APIRouter(tags=["catalog"])


@router.get("/partners")
def partners(
    db: Session = Depends(get_db), user: User = Depends(require_access("catalog.read"))
):
    query = select(Organization)
    if user.role != "WAREHOUSE_ADMIN":
        ids = memberships(db, user)
        related = (
            db.scalars(
                select(SupplyRelationship.owner_id).where(
                    SupplyRelationship.supplier_id.in_(ids)
                )
            ).all()
            if user.role == "SUPPLIER"
            else []
        )
        query = query.where(Organization.id.in_([*ids, *related]))
    return [org_dto(org) for org in db.scalars(query).all()]


@router.post("/partners", status_code=201)
def create_partner(
    cmd: PartnerCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("catalog.manage")),
):
    def apply():
        org = Organization(name=cmd.name.strip(), kind=cmd.kind)
        db.add(org)
        db.flush()
        return org_dto(org)

    return execute(
        db, user.id, key, "partner.create", "partners", cmd.model_dump(), {}, apply
    )


@router.get("/skus")
def skus(
    db: Session = Depends(get_db), user: User = Depends(require_access("catalog.read"))
):
    query = select(Sku)
    if user.role == "RETAILER_OWNER":
        query = query.where(Sku.owner_id.in_(memberships(db, user)))
    elif user.role == "SUPPLIER":
        query = query.where(
            Sku.id.in_(
                select(SupplyRelationship.sku_id).where(
                    SupplyRelationship.supplier_id.in_(memberships(db, user))
                )
            )
        )
    return [sku_dto(sku) for sku in db.scalars(query).all()]


@router.post("/skus", status_code=201)
def create_sku(
    cmd: SkuCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("catalog.manage")),
):
    def apply():
        owner = db.get(Organization, cmd.owner_id)
        if not owner or owner.kind != "RETAILER" or not owner.active:
            raise HTTPException(422, "Chủ hàng không hợp lệ")
        sku = Sku(**cmd.model_dump())
        db.add(sku)
        db.flush()
        return sku_dto(sku)

    return execute(db, user.id, key, "sku.create", "skus", cmd.model_dump(), {}, apply)


@router.get("/warehouses")
def warehouses(
    db: Session = Depends(get_db), user: User = Depends(require_access("catalog.read"))
):
    return [
        {"id": w.id, "name": w.name}
        for w in db.scalars(
            select(Warehouse).where(Warehouse.name == user.warehouse_scope)
        ).all()
    ]


@router.post("/warehouses", status_code=201)
def add_warehouse(
    cmd: WarehouseCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("catalog.manage")),
):
    return execute(
        db,
        user.id,
        key,
        "warehouse.create",
        "warehouses",
        cmd.model_dump(),
        {},
        lambda: create_warehouse(db, user, cmd),
    )


@router.get("/locations")
def locations(
    db: Session = Depends(get_db), user: User = Depends(require_access("catalog.read"))
):
    rows = db.scalars(
        select(StorageLocation)
        .join(Warehouse, Warehouse.id == StorageLocation.warehouse_id)
        .where(Warehouse.name == user.warehouse_scope)
    ).all()
    return [{"id": l.id, "warehouseId": l.warehouse_id, "code": l.code} for l in rows]


@router.post("/locations", status_code=201)
def create_location(
    cmd: LocationCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("catalog.manage")),
):
    def apply():
        warehouse(db, user, cmd.warehouse_id)
        location = StorageLocation(**cmd.model_dump())
        db.add(location)
        db.flush()
        return {
            "id": location.id,
            "warehouseId": location.warehouse_id,
            "code": location.code,
        }

    return execute(
        db, user.id, key, "location.create", "locations", cmd.model_dump(), {}, apply
    )


@router.post("/supply-relationships", status_code=201)
def create_supply(
    cmd: SupplyCreate,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("catalog.manage")),
):
    def apply():
        supplier = db.get(Organization, cmd.supplier_id)
        owner = db.get(Organization, cmd.owner_id)
        sku = db.get(Sku, cmd.sku_id)
        if (
            not supplier
            or supplier.kind != "SUPPLIER"
            or not owner
            or owner.kind != "RETAILER"
            or not sku
            or sku.owner_id != owner.id
        ):
            raise HTTPException(422, "Quan hệ cung ứng không hợp lệ")
        relationship = SupplyRelationship(**cmd.model_dump())
        db.add(relationship)
        db.flush()
        return {"id": relationship.id, **cmd.model_dump()}

    return execute(
        db,
        user.id,
        key,
        "supply.create",
        "supply-relationships",
        cmd.model_dump(),
        {},
        apply,
    )


@router.get("/supply-relationships")
def supply_relationships(
    db: Session = Depends(get_db), user: User = Depends(require_access("catalog.read"))
):
    query = select(SupplyRelationship)
    if user.role == "SUPPLIER":
        query = query.where(SupplyRelationship.supplier_id.in_(memberships(db, user)))
    elif user.role == "RETAILER_OWNER":
        query = query.where(SupplyRelationship.owner_id.in_(memberships(db, user)))
    return [
        {
            "id": r.id,
            "supplier_id": r.supplier_id,
            "owner_id": r.owner_id,
            "sku_id": r.sku_id,
        }
        for r in db.scalars(query).all()
    ]

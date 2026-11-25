from fastapi import HTTPException
from sqlalchemy import select
import uuid
from app.modules.inventory.models import Warehouse
from .models import Organization, PartnerMembership, Sku, SupplyRelationship


def memberships(db, user):
    return list(
        db.scalars(
            select(PartnerMembership.organization_id).where(
                PartnerMembership.user_id == user.id
            )
        ).all()
    )


def warehouse(db, user, warehouse_id):
    result = db.get(Warehouse, warehouse_id)
    if not result or result.name != user.warehouse_scope:
        raise HTTPException(404, "Kho không thuộc phạm vi được cấp")
    return result


def owner_scope(db, user, owner_id):
    owner = db.get(Organization, owner_id)
    if not owner or not owner.active or owner.kind != "RETAILER":
        raise HTTPException(422, "Chủ hàng không hợp lệ")
    if user.role != "WAREHOUSE_ADMIN" and owner_id not in memberships(db, user):
        raise HTTPException(404, "Chủ hàng không thuộc tài khoản của bạn")
    return owner


def supplier_scope(db, user, supplier_id, owner_id, sku_ids):
    supplier = db.get(Organization, supplier_id)
    if not supplier or not supplier.active or supplier.kind != "SUPPLIER":
        raise HTTPException(422, "Nhà cung cấp không hợp lệ")
    if user.role != "WAREHOUSE_ADMIN" and supplier_id not in memberships(db, user):
        raise HTTPException(404, "Nhà cung cấp không thuộc tài khoản của bạn")
    allowed = set(
        db.scalars(
            select(SupplyRelationship.sku_id).where(
                SupplyRelationship.supplier_id == supplier_id,
                SupplyRelationship.owner_id == owner_id,
            )
        ).all()
    )
    if not set(sku_ids).issubset(allowed):
        raise HTTPException(403, "Chưa có quan hệ cung ứng cho SKU và chủ hàng đã chọn")


def validate_lines(db, owner_id, lines):
    owner = db.get(Organization, owner_id)
    if not owner or not owner.active or owner.kind != "RETAILER":
        raise HTTPException(422, "Chủ hàng không hợp lệ hoặc đã ngừng hoạt động")
    if not lines or len({line.sku_id for line in lines}) != len(lines):
        raise HTTPException(422, "Danh sách hàng trống hoặc trùng SKU")
    for line in lines:
        sku = db.get(Sku, line.sku_id)
        if not sku or sku.owner_id != owner_id:
            raise HTTPException(422, "SKU không thuộc chủ hàng của chứng từ")


def org_dto(org):
    return {"id": org.id, "name": org.name, "kind": org.kind, "active": org.active}


def sku_dto(sku):
    return {
        "id": sku.id,
        "code": sku.code,
        "name": sku.name,
        "baseUnit": sku.base_unit,
        "ownerId": sku.owner_id,
    }


def create_warehouse(db, user, cmd):
    if db.scalar(select(Warehouse).where(Warehouse.name == user.warehouse_scope)):
        raise HTTPException(
            409, "Tài khoản đã được gán kho; chưa hỗ trợ tạo thêm kho ngoài phạm vi"
        )
    record = Warehouse(id=str(uuid.uuid4()), name=cmd.name)
    db.add(record)
    user.warehouse_scope = cmd.name
    db.flush()
    return {"id": record.id, "name": record.name}

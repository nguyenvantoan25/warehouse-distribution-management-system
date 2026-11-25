from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from .models import InventoryBalance, InventoryPosting, InboundPosting, Warehouse
from app.modules.catalog.service import memberships
from app.modules.catalog.models import Sku, Organization, StorageLocation
from .models import BalanceLocation
from .service import scoped_balances, balance_dto, hold_stock
from .schemas import HoldCommand

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/balances")
def balances(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inventory.read")),
):
    result = []
    owners = memberships(db, user) if user.role == "RETAILER_OWNER" else None
    for balance in scoped_balances(db, user.warehouse_scope):
        if owners is not None and balance.owner_id not in owners:
            continue
        sku = db.scalar(select(Sku).where(Sku.code == balance.sku_code))
        owner = db.get(Organization, balance.owner_id)
        location = db.scalar(
            select(StorageLocation)
            .join(BalanceLocation, BalanceLocation.location_id == StorageLocation.id)
            .where(BalanceLocation.balance_id == balance.id)
        )
        result.append(
            {
                **balance_dto(balance),
                "skuName": sku.name if sku else balance.sku_code,
                "unit": sku.base_unit if sku else "đơn vị",
                "ownerName": owner.name if owner else balance.owner_id,
                "locationCode": location.code if location else "Chưa xác định",
            }
        )
    return result


@router.get("/movements")
def movements(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inventory.read")),
):
    result = []
    for model, kind in [
        (InventoryPosting, "HANDOVER_ISSUE"),
        (InboundPosting, "INBOUND"),
    ]:
        query = (
            select(model, InventoryBalance)
            .join(InventoryBalance, InventoryBalance.id == model.balance_id)
            .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
            .where(Warehouse.name == user.warehouse_scope)
        )
        if user.role == "RETAILER_OWNER":
            query = query.where(InventoryBalance.owner_id.in_(memberships(db, user)))
        for posting, balance in db.execute(query).all():
            result.append(
                {
                    "id": posting.id,
                    "skuCode": balance.sku_code,
                    "ownerId": balance.owner_id,
                    "quantity": posting.quantity,
                    "kind": kind,
                    "at": posting.at.isoformat() + "Z",
                }
            )
    return sorted(result, key=lambda row: row["at"], reverse=True)


from fastapi import Header, HTTPException
from sqlalchemy import update
from app.core.commands import execute


@router.post("/holds")
def hold(
    cmd: HoldCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inventory.manage")),
):
    balance, before, apply = hold_stock(db, user, cmd)
    return execute(
        db,
        user.id,
        key,
        "inventory.release" if cmd.release else "inventory.hold",
        balance.id,
        cmd.model_dump(),
        before,
        apply,
    )

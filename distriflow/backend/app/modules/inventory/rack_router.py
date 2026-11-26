from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.commands import execute
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from .rack_schemas import RackInitializeCommand
from .rack_service import initialize_racks, rack_map, scoped_warehouse

router = APIRouter(prefix="/inventory/rack-map", tags=["warehouse-racks"])


@router.get("")
def read_map(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inventory.manage")),
):
    # The complete physical occupancy is private to warehouse operations, not partners.
    return rack_map(db, user)


@router.post("/initialize")
def initialize(
    cmd: RackInitializeCommand,
    key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    user: User = Depends(require_access("inventory.manage")),
):
    scoped_warehouse(db, user, cmd.warehouse_id)
    return execute(
        db,
        user.id,
        key,
        "rack.initialize.single",
        cmd.warehouse_id,
        cmd.model_dump(),
        {},
        lambda: initialize_racks(db, user, cmd),
    )

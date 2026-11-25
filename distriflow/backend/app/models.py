"""SQLAlchemy model registry used by versioned PostgreSQL migrations and tests."""

from app.core.commands import AuditLog, CommandReceipt
from app.modules.auth.models import User, AccessSession
from app.modules.dispatch.models import PickupTask, Package
from app.modules.handover.models import (
    PackageScan,
    HandoverConfirmation,
    Receipt,
    IdempotencyRequest,
)
from app.modules.catalog.models import (
    Organization,
    PartnerMembership,
    Sku,
    SupplyRelationship,
    StorageLocation,
)
from app.modules.inventory.models import (
    InventoryBalance,
    Warehouse,
    StockReservation,
    InventoryPosting,
    BalanceLocation,
    InboundPosting,
    StockMovement,
)
from app.modules.inbound.models import InboundRequest, InboundLine
from app.modules.outbound.models import (
    OutboundRequest,
    OutboundLine,
    OutboundAllocation,
    OutboundTask,
    PackageItem,
)

"""Domain routers keep their own access, warehouse and organization checks."""

from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.auth.scopes import router as account_scopes_router
from app.modules.catalog.router import router as catalog_router
from app.modules.dispatch.router import router as dispatch_router
from app.modules.handover.router import router as handover_router
from app.modules.inbound.router import router as inbound_router
from app.modules.inventory.router import router as inventory_router
from app.modules.inventory.rack_router import router as rack_router
from app.modules.directory.router import router as directory_router
from app.modules.outbound.router import router as outbound_router
from app.modules.platform.router import router as platform_router

router = APIRouter(prefix="/api/v1")
for domain_router in (
    auth_router,
    account_scopes_router,
    directory_router,
    platform_router,
    dispatch_router,
    inventory_router,
    rack_router,
    catalog_router,
    inbound_router,
    outbound_router,
    handover_router,
):
    router.include_router(domain_router)

"""Isolated local API for browser tests; never opens the user's database."""

import os
import uuid
from pathlib import Path

runtime = Path(__file__).resolve().parents[1] / ".runtime"
runtime.mkdir(exist_ok=True)
os.environ["DATABASE_URL"] = (
    "sqlite:///" + (runtime / f"e2e-{uuid.uuid4().hex}.sqlite").as_posix()
)
from app import models
from app.core.database import Base, SessionLocal, engine
from app.modules.auth.access import password_hash

Base.metadata.create_all(engine)
with SessionLocal() as db:
    for username, role in [
        ("admin", "WAREHOUSE_ADMIN"),
        ("supplier", "SUPPLIER"),
        ("retailer", "RETAILER_OWNER"),
        ("shipper", "SHIPPER"),
        ("empty-admin", "WAREHOUSE_ADMIN"),
        ("unassigned-shipper", "SHIPPER"),
    ]:
        db.add(
            models.User(
                id="e2e-" + username,
                username="e2e-" + username,
                password_hash=password_hash("e2e-only-password-29"),
                role=role,
                warehouse_scope=(
                    ""
                    if username in {"empty-admin", "unassigned-shipper"}
                    else "Kho kiểm thử"
                ),
            )
        )
    db.add_all(
        [
            models.Warehouse(id="e2e-wh", name="Kho kiểm thử"),
            models.Organization(
                id="e2e-owner", name="Chủ hàng kiểm thử", kind="RETAILER"
            ),
            models.Organization(
                id="e2e-supplier-org", name="Nhà cung cấp kiểm thử", kind="SUPPLIER"
            ),
        ]
    )
    db.flush()
    db.add_all(
        [
            models.Sku(
                id="e2e-sku",
                code="E2E-SKU",
                name="Hàng kiểm thử",
                base_unit="chiếc",
                owner_id="e2e-owner",
            ),
            models.StorageLocation(
                id="e2e-location", warehouse_id="e2e-wh", code="TEST-A01"
            ),
            models.PartnerMembership(
                user_id="e2e-supplier", organization_id="e2e-supplier-org"
            ),
            models.PartnerMembership(
                user_id="e2e-retailer", organization_id="e2e-owner"
            ),
        ]
    )
    db.flush()
    db.add(
        models.SupplyRelationship(
            supplier_id="e2e-supplier-org", owner_id="e2e-owner", sku_id="e2e-sku"
        )
    )
    db.commit()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8001)

"""Explicit, additive local setup. Existing accounts and business records are preserved."""

import json
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime
from sqlalchemy import inspect, select
from app.core.config import BACKEND_DIR
from app.core.database import Base, SessionLocal, engine
from app import models
from app.modules.auth.access import password_hash


def main():
    import sys

    if "--confirm-demo" not in sys.argv or engine.dialect.name != "sqlite":
        raise SystemExit(
            "Demo data is allowed only in an explicit SQLite sandbox with --confirm-demo."
        )
    if (
        engine.dialect.name == "sqlite"
        and Path(engine.url.database).exists()
        and not inspect(engine).has_table("organizations")
    ):
        backup_dir = BACKEND_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        with sqlite3.connect(engine.url.database) as source, sqlite3.connect(
            backup_dir / f"before-modules-{datetime.now():%Y%m%d-%H%M%S}.sqlite"
        ) as destination:
            source.backup(destination)
        print("Backed up existing SQLite database to backend/backups/.")
    Base.metadata.create_all(engine)
    credentials = []
    with SessionLocal() as db:
        for username, role, user_id in [
            ("admin", "WAREHOUSE_ADMIN", "warehouse-admin-demo"),
            ("dispatch", "DISPATCH_MANAGER", "dispatch-demo"),
            ("shipper", "SHIPPER", "shipper-demo"),
            ("supplier", "SUPPLIER", "supplier-demo"),
            ("retailer", "RETAILER_OWNER", "retailer-demo"),
        ]:
            if not db.get(models.User, user_id):
                password = secrets.token_urlsafe(15)
                db.add(
                    models.User(
                        id=user_id,
                        username=username,
                        password_hash=password_hash(password),
                        role=role,
                        warehouse_scope="Kho Trung tâm Quận 7",
                    )
                )
                credentials.append(
                    {"username": username, "password": password, "role": role}
                )
        if not db.get(models.Warehouse, "WH-HCM"):
            db.add(models.Warehouse(id="WH-HCM", name="Kho Trung tâm Quận 7"))
        for org_id, name, kind in [
            ("retailer-a", "Chủ hàng Minh Phát", "RETAILER"),
            ("supplier-a", "Nhà cung cấp An Phú", "SUPPLIER"),
        ]:
            if not db.get(models.Organization, org_id):
                db.add(models.Organization(id=org_id, name=name, kind=kind))
        db.flush()
        if not db.get(models.Sku, "sku-cafe-demo"):
            db.add(
                models.Sku(
                    id="sku-cafe-demo",
                    code="SKU-CAFE",
                    name="Cà phê rang xay",
                    base_unit="gói",
                    owner_id="retailer-a",
                )
            )
        for user_id, org_id in [
            ("supplier-demo", "supplier-a"),
            ("retailer-demo", "retailer-a"),
        ]:
            if not db.get(models.PartnerMembership, (user_id, org_id)):
                db.add(
                    models.PartnerMembership(user_id=user_id, organization_id=org_id)
                )
        db.flush()
        if not db.scalar(
            select(models.SupplyRelationship).where(
                models.SupplyRelationship.supplier_id == "supplier-a",
                models.SupplyRelationship.sku_id == "sku-cafe-demo",
            )
        ):
            db.add(
                models.SupplyRelationship(
                    supplier_id="supplier-a",
                    owner_id="retailer-a",
                    sku_id="sku-cafe-demo",
                )
            )
        if not db.get(models.StorageLocation, "location-demo"):
            db.add(
                models.StorageLocation(
                    id="location-demo", warehouse_id="WH-HCM", code="A-01"
                )
            )
        db.flush()
        task = db.scalar(
            select(models.PickupTask).where(models.PickupTask.code == "PK-2026-0001")
        )
        if not task and not db.scalar(select(models.PickupTask).limit(1)):
            task = models.PickupTask(
                code="PK-2026-0001",
                warehouse_name="Kho Trung tâm Quận 7",
                shipper_id="shipper-demo",
            )
            db.add(task)
            db.flush()
            db.add_all(
                [
                    models.Package(task_id=task.id, code=f"PKG-{i:03}")
                    for i in range(1, 4)
                ]
            )
        balance = db.scalar(
            select(models.InventoryBalance).where(
                models.InventoryBalance.owner_id == "retailer-a",
                models.InventoryBalance.sku_code == "SKU-CAFE",
                models.InventoryBalance.warehouse_id == "WH-HCM",
            )
        )
        if not balance:
            balance = models.InventoryBalance(
                owner_id="retailer-a",
                sku_code="SKU-CAFE",
                warehouse_id="WH-HCM",
                on_hand=120,
                reserved=30,
                unavailable=5,
            )
            db.add(balance)
            db.flush()
        if not db.get(models.BalanceLocation, balance.id):
            db.add(
                models.BalanceLocation(
                    balance_id=balance.id, location_id="location-demo"
                )
            )
        if (
            task
            and task.status != "handed_over"
            and balance.reserved >= 30
            and not db.scalar(
                select(models.StockReservation).where(
                    models.StockReservation.task_id == task.id
                )
            )
        ):
            db.add(
                models.StockReservation(
                    task_id=task.id, balance_id=balance.id, quantity=30
                )
            )
        db.commit()
    if credentials:
        path = BACKEND_DIR / "accounts.local.json"
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        names = {item["username"] for item in existing}
        existing += [item for item in credentials if item["username"] not in names]
        path.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            "New local accounts: "
            + ", ".join(item["username"] for item in credentials)
            + ". See backend/accounts.local.json."
        )
    else:
        print("Local setup ready; existing passwords and records preserved.")


if __name__ == "__main__":
    main()

"""Android emulator fixture. Imports the SQLite-only E2E setup, never PostgreSQL."""
from tests import serve_e2e
from app import models
from app.core.database import SessionLocal, engine

if engine.dialect.name != "sqlite":
    raise SystemExit("Android UI fixtures must not use PostgreSQL")

with SessionLocal.begin() as db:
    task = models.PickupTask(id="android-task", code="ANDROID-TEST-001",
        warehouse_name="Kho kiểm thử", shipper_id="e2e-shipper")
    db.add(task)
    db.flush()
    db.add_all([models.Package(task_id=task.id, code=code) for code in ["ANDROID-PKG-001", "ANDROID-PKG-002"]])
    balance = models.InventoryBalance(owner_id="e2e-owner", sku_code="E2E-SKU", warehouse_id="e2e-wh",
        on_hand=20, reserved=5, unavailable=0)
    db.add(balance)
    db.flush()
    db.add(models.StockReservation(task_id=task.id, balance_id=balance.id, quantity=5))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001)

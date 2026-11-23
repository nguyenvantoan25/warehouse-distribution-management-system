import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def uid() -> str: return str(uuid.uuid4())
class InventoryBalance(Base):
    __tablename__='inventory_balances'
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); owner_id: Mapped[str]=mapped_column(String,index=True)
    sku_code: Mapped[str]=mapped_column(String); warehouse_id: Mapped[str]=mapped_column(String); on_hand: Mapped[int]=mapped_column(Integer,default=0); reserved: Mapped[int]=mapped_column(Integer,default=0); unavailable: Mapped[int]=mapped_column(Integer,default=0)
class PickupTask(Base):
    __tablename__='pickup_tasks'
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); code: Mapped[str]=mapped_column(String,unique=True)
    warehouse_name: Mapped[str]=mapped_column(String); shipper_id: Mapped[str]=mapped_column(String,index=True); status: Mapped[str]=mapped_column(String,default='ready_for_handover'); version: Mapped[int]=mapped_column(Integer,default=1)
    shipper_accepted: Mapped[bool]=mapped_column(Boolean,default=False); arrived_at_warehouse: Mapped[bool]=mapped_column(Boolean,default=False)
class Package(Base):
    __tablename__='packages'
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); task_id: Mapped[str]=mapped_column(ForeignKey('pickup_tasks.id'),index=True); code: Mapped[str]=mapped_column(String,unique=True)
class PackageScan(Base):
    __tablename__='package_scans'; __table_args__=(UniqueConstraint('task_id','package_id',name='uq_task_package_scan'),)
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); task_id: Mapped[str]=mapped_column(ForeignKey('pickup_tasks.id')); package_id: Mapped[str]=mapped_column(ForeignKey('packages.id')); at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class HandoverConfirmation(Base):
    __tablename__='handover_confirmations'; __table_args__=(UniqueConstraint('task_id','side','version',name='uq_confirmation_version'),)
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); task_id: Mapped[str]=mapped_column(ForeignKey('pickup_tasks.id')); side: Mapped[str]=mapped_column(String); version: Mapped[int]=mapped_column(Integer); actor_id: Mapped[str]=mapped_column(String); at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Receipt(Base):
    __tablename__='handover_receipts'
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); task_id: Mapped[str]=mapped_column(ForeignKey('pickup_tasks.id'),unique=True); number: Mapped[str]=mapped_column(String,unique=True); issued_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class StockMovement(Base):
    __tablename__='stock_movements'; __table_args__=(UniqueConstraint('source_task_id','kind',name='uq_stock_issue_per_task'),)
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); source_task_id: Mapped[str]=mapped_column(String); kind: Mapped[str]=mapped_column(String); quantity: Mapped[int]=mapped_column(Integer); at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class IdempotencyRequest(Base):
    __tablename__='idempotency_requests'; __table_args__=(UniqueConstraint('actor_id','key',name='uq_actor_idempotency'),)
    id: Mapped[str]=mapped_column(String,primary_key=True,default=uid); actor_id: Mapped[str]=mapped_column(String); key: Mapped[str]=mapped_column(String); task_id: Mapped[str]=mapped_column(String); response_status: Mapped[str]=mapped_column(String)

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import Base, engine, get_db
from app.modules.handover.models import HandoverConfirmation, IdempotencyRequest, InventoryBalance, Package, PackageScan, PickupTask, Receipt, StockMovement

class VersionedCommand(BaseModel): version: int = Field(ge=1)
class RespondCommand(VersionedCommand): accepted: bool
class ScanCommand(VersionedCommand): package_code: str = Field(min_length=1,max_length=80)
class TaskDto(BaseModel):
    id:str; code:str; warehouseName:str; packages:list[str]; status:str; shipperAccepted:bool; arrivedAtWarehouse:bool; scannedCodes:list[str]; version:int
def task_dto(db:Session, task:PickupTask)->TaskDto:
    packages=db.scalars(select(Package).where(Package.task_id==task.id)).all(); scanned={x.package_id for x in db.scalars(select(PackageScan).where(PackageScan.task_id==task.id)).all()}
    return TaskDto(id=task.id,code=task.code,warehouseName=task.warehouse_name,packages=[x.code for x in packages],status=task.status,shipperAccepted=task.shipper_accepted,arrivedAtWarehouse=task.arrived_at_warehouse,scannedCodes=[x.code for x in packages if x.id in scanned],version=task.version)
def actor(x_demo_actor:str|None=Header(default=None))->str:
    # Development adapter. Production replaces this dependency with verified HttpOnly-session identity.
    if not x_demo_actor: raise HTTPException(401,detail={'error':{'code':'AUTH_REQUIRED','message':'Bạn cần đăng nhập'}})
    return x_demo_actor
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(engine) # local-demo bootstrap; deploy through Alembic migration in production
    db=next(get_db())
    if not db.scalar(select(PickupTask).limit(1)):
        task=PickupTask(code='PK-2026-0001',warehouse_name='Kho Trung tâm Quận 7',shipper_id='shipper-demo'); db.add(task); db.flush()
        db.add_all([Package(task_id=task.id,code='PKG-001'),Package(task_id=task.id,code='PKG-002'),Package(task_id=task.id,code='PKG-003'),InventoryBalance(owner_id='retailer-a',sku_code='SKU-CAFE',warehouse_id='WH-HCM',on_hand=120,reserved=30,unavailable=5)]); db.commit()
    db.close(); yield
app=FastAPI(title='DistriFlow API',version='0.1.0',lifespan=lifespan)
def require_task(db:Session,task_id:str,actor_id:str)->PickupTask:
    task=db.get(PickupTask,task_id)
    if not task or task.shipper_id!=actor_id: raise HTTPException(404,detail={'error':{'code':'TASK_NOT_FOUND','message':'Không tìm thấy nhiệm vụ trong phạm vi của bạn'}})
    return task
def check_version(task:PickupTask, version:int):
    if task.version!=version: raise HTTPException(409,detail={'error':{'code':'VERSION_CONFLICT','message':'Phiên đã thay đổi, hãy tải lại'}})
@app.get('/api/v1/dashboard')
def dashboard(db:Session=Depends(get_db), x_demo_actor:str=Depends(actor)):
    balances=db.scalars(select(InventoryBalance)).all(); tasks=db.scalars(select(PickupTask)).all()
    return {'available':sum(x.on_hand-x.reserved-x.unavailable for x in balances),'reserved':sum(x.reserved for x in balances),'pendingOutbound':1,'readyHandover':sum(x.status=='ready_for_handover' for x in tasks),'tasks':[task_dto(db,x).model_dump() for x in tasks]}
@app.get('/api/v1/pickup-tasks')
def my_tasks(mine:bool=True,db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)): return [task_dto(db,x).model_dump() for x in db.scalars(select(PickupTask).where(PickupTask.shipper_id==x_demo_actor)).all()]
def idempotent(db:Session,actor_id:str,key:str|None,task:PickupTask):
    if not key: raise HTTPException(400,detail={'error':{'code':'IDEMPOTENCY_KEY_REQUIRED','message':'Thiếu Idempotency-Key'}})
    old=db.scalar(select(IdempotencyRequest).where(IdempotencyRequest.actor_id==actor_id,IdempotencyRequest.key==key))
    return old is not None
@app.post('/api/v1/pickup-tasks/{task_id}/respond',response_model=TaskDto)
def respond(task_id:str,cmd:RespondCommand,idempotency_key:str|None=Header(default=None),db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)):
    task=require_task(db,task_id,x_demo_actor)
    if idempotent(db,x_demo_actor,idempotency_key,task): return task_dto(db,task)
    check_version(task,cmd.version)
    if not cmd.accepted: raise HTTPException(409,detail={'error':{'code':'DECLINE_NEEDS_REASSIGNMENT','message':'Từ chối cần điều phối lại, không tự đổi phương án'}})
    task.shipper_accepted=True; task.version+=1; db.add(IdempotencyRequest(actor_id=x_demo_actor,key=idempotency_key,task_id=task.id,response_status='ok')); db.commit(); return task_dto(db,task)
@app.post('/api/v1/pickup-tasks/{task_id}/arrive',response_model=TaskDto)
def arrive(task_id:str,cmd:VersionedCommand,idempotency_key:str|None=Header(default=None),db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)):
    task=require_task(db,task_id,x_demo_actor)
    if idempotent(db,x_demo_actor,idempotency_key,task): return task_dto(db,task)
    check_version(task,cmd.version)
    if not task.shipper_accepted: raise HTTPException(409,detail={'error':{'code':'TASK_NOT_ACCEPTED','message':'Cần nhận nhiệm vụ trước'}})
    task.arrived_at_warehouse=True; task.version+=1; db.add(IdempotencyRequest(actor_id=x_demo_actor,key=idempotency_key,task_id=task.id,response_status='ok')); db.commit(); return task_dto(db,task)
@app.post('/api/v1/pickup-tasks/{task_id}/scan',response_model=TaskDto)
def scan(task_id:str,cmd:ScanCommand,idempotency_key:str|None=Header(default=None),db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)):
    task=require_task(db,task_id,x_demo_actor)
    if idempotent(db,x_demo_actor,idempotency_key,task): return task_dto(db,task)
    check_version(task,cmd.version)
    if not task.arrived_at_warehouse: raise HTTPException(409,detail={'error':{'code':'NOT_ARRIVED','message':'Chỉ quét khi đã đến kho'}})
    package=db.scalar(select(Package).where(Package.task_id==task.id,Package.code==cmd.package_code))
    if not package: raise HTTPException(422,detail={'error':{'code':'INVALID_PACKAGE','message':'Mã kiện không thuộc phiên bàn giao'}})
    if db.scalar(select(PackageScan).where(PackageScan.task_id==task.id,PackageScan.package_id==package.id)): raise HTTPException(409,detail={'error':{'code':'DUPLICATE_SCAN','message':'Kiện đã được quét, tiến độ không thay đổi'}})
    db.add(PackageScan(task_id=task.id,package_id=package.id)); task.version+=1; db.add(IdempotencyRequest(actor_id=x_demo_actor,key=idempotency_key,task_id=task.id,response_status='ok')); db.commit(); return task_dto(db,task)
@app.post('/api/v1/pickup-tasks/{task_id}/shipper-confirm',response_model=TaskDto)
def shipper_confirm(task_id:str,cmd:VersionedCommand,idempotency_key:str|None=Header(default=None),db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)):
    task=require_task(db,task_id,x_demo_actor)
    if idempotent(db,x_demo_actor,idempotency_key,task): return task_dto(db,task)
    check_version(task,cmd.version)
    package_count=len(db.scalars(select(Package).where(Package.task_id==task.id)).all()); scanned_count=len(db.scalars(select(PackageScan).where(PackageScan.task_id==task.id)).all())
    if scanned_count!=package_count: raise HTTPException(409,detail={'error':{'code':'PACKAGES_INCOMPLETE','message':'Chưa quét đủ kiện, không thể xác nhận'}})
    db.add(HandoverConfirmation(task_id=task.id,side='shipper',version=task.version,actor_id=x_demo_actor)); task.status='pending_confirmations'; task.version+=1; db.add(IdempotencyRequest(actor_id=x_demo_actor,key=idempotency_key,task_id=task.id,response_status='pending')); db.commit(); return task_dto(db,task)
@app.post('/api/v1/pickup-tasks/{task_id}/warehouse-confirm',response_model=TaskDto)
def warehouse_confirm(task_id:str,cmd:VersionedCommand,idempotency_key:str|None=Header(default=None),db:Session=Depends(get_db),x_demo_actor:str=Depends(actor)):
    if x_demo_actor != 'warehouse-admin-demo': raise HTTPException(403,detail={'error':{'code':'FORBIDDEN','message':'Chỉ kho được xác nhận phía kho'}})
    task=db.get(PickupTask,task_id)
    if not task: raise HTTPException(404,detail={'error':{'code':'TASK_NOT_FOUND','message':'Không tìm thấy phiên bàn giao'}})
    if idempotent(db,x_demo_actor,idempotency_key,task): return task_dto(db,task)
    check_version(task,cmd.version)
    shipper_ok=db.scalar(select(HandoverConfirmation).where(HandoverConfirmation.task_id==task.id,HandoverConfirmation.side=='shipper'))
    if not shipper_ok: raise HTTPException(409,detail={'error':{'code':'SHIPPER_CONFIRM_REQUIRED','message':'Đang chờ shipper xác nhận'}})
    # Một giao dịch duy nhất: ghi nhận kho, phát sinh chứng từ và ghi xuất đúng một lần.
    db.add(HandoverConfirmation(task_id=task.id,side='warehouse',version=task.version,actor_id=x_demo_actor))
    if not db.scalar(select(Receipt).where(Receipt.task_id==task.id)):
        package_count=len(db.scalars(select(Package).where(Package.task_id==task.id)).all())
        balance=db.scalar(select(InventoryBalance).where(InventoryBalance.owner_id=='retailer-a').with_for_update())
        if not balance or balance.reserved < package_count or balance.on_hand < package_count: raise HTTPException(409,detail={'error':{'code':'RESERVATION_INVALID','message':'Lượng giữ không còn hợp lệ'}})
        balance.on_hand-=package_count; balance.reserved-=package_count
        db.add_all([StockMovement(source_task_id=task.id,kind='HANDOVER_ISSUE',quantity=package_count),Receipt(task_id=task.id,number=f'BBBG-{task.code}')])
    task.status='handed_over'; task.version+=1; db.add(IdempotencyRequest(actor_id=x_demo_actor,key=idempotency_key,task_id=task.id,response_status='handed_over')); db.commit(); return task_dto(db,task)

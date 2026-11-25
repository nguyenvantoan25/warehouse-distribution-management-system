from pydantic import BaseModel, Field
from app.core.schemas import VersionedCommand


class RespondCommand(VersionedCommand):
    accepted: bool


class AssignCommand(VersionedCommand):
    shipper_id: str = Field(min_length=1, max_length=100)


class TaskDto(BaseModel):
    receiptId: str | None = None
    id: str
    code: str
    warehouseName: str
    packages: list[str]
    status: str
    shipperAccepted: bool
    arrivedAtWarehouse: bool
    scannedCodes: list[str]
    version: int
    shipperId: str
    shipperName: str

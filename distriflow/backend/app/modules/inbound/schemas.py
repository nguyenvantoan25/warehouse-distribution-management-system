from pydantic import BaseModel, Field
from app.core.schemas import VersionedCommand, RequestLine


class InboundCreate(BaseModel):
    supplier_id: str
    owner_id: str
    warehouse_id: str
    lines: list[RequestLine] = Field(min_length=1, max_length=100)


class ReviewCommand(VersionedCommand):
    accepted: bool = True
    note: str = Field(default="", max_length=1000)


class ReceivedLine(BaseModel):
    line_id: str
    good: int = Field(ge=0)
    quarantined: int = Field(ge=0)


class ReceiveCommand(VersionedCommand):
    lines: list[ReceivedLine] = Field(min_length=1, max_length=100)
    note: str = Field(default="", max_length=1000)


class PutawayCommand(VersionedCommand):
    location_id: str

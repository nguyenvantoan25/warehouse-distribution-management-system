from typing import Literal
from pydantic import BaseModel, Field
from app.core.schemas import RequestLine
from app.core.schemas import VersionedCommand


class OutboundCreate(BaseModel):
    owner_id: str
    warehouse_id: str
    shipper_mode: Literal["DISTRIFLOW", "OWNER_ASSIGNED"] = "DISTRIFLOW"
    shipper_id: str = ""
    lines: list[RequestLine] = Field(min_length=1, max_length=100)


class PackCommand(VersionedCommand):
    package_count: int = Field(ge=1, le=100)

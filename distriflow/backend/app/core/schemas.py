"""Small shared command primitives; no domain-to-domain schema dependency."""

from pydantic import BaseModel, Field


class VersionedCommand(BaseModel):
    version: int = Field(ge=1)


class RequestLine(BaseModel):
    sku_id: str
    quantity: int = Field(gt=0, le=10000000)

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class CatalogCommand(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class PartnerCreate(CatalogCommand):
    name: str = Field(min_length=2, max_length=150)
    kind: Literal["RETAILER", "SUPPLIER"]


class SkuCreate(CatalogCommand):
    code: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=2, max_length=150)
    base_unit: str = Field(min_length=1, max_length=30)
    owner_id: str


class SupplyCreate(CatalogCommand):
    supplier_id: str
    owner_id: str
    sku_id: str


class LocationCreate(CatalogCommand):
    warehouse_id: str
    code: str = Field(min_length=1, max_length=40)


class WarehouseCreate(CatalogCommand):
    name: str = Field(min_length=2, max_length=150)

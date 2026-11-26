from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class RackInitializeCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: str = Field(min_length=1)
    total_positions: Literal[800]

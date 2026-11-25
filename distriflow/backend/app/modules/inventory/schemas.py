from pydantic import BaseModel, Field


class HoldCommand(BaseModel):
    balance_id: str
    quantity: int = Field(gt=0)
    release: bool = False
    reason: str = Field(min_length=3, max_length=500)

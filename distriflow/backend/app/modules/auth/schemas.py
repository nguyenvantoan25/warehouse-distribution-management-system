from pydantic import BaseModel, Field


class LoginCommand(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=256)


class ScopeCommand(BaseModel):
    warehouse_id: str
    organization_id: str | None = None

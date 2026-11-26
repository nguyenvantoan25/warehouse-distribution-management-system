from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

ManagedRole = Literal["SHIPPER", "SUPPLIER", "RETAILER_OWNER"]


class ProfileFields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    name: str = Field(min_length=2, max_length=150)
    supplied_goods: str | None = Field(default=None, max_length=1000)

    @field_validator("name", "supplied_goods")
    @classmethod
    def trim_text(cls, value):
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Không được để trống")
        return value

    @field_validator("name")
    @classmethod
    def valid_name(cls, value):
        if len(value) < 2:
            raise ValueError("Tên cần ít nhất 2 ký tự")
        return value

    @field_validator("password", check_fields=False)
    @classmethod
    def valid_password(cls, value):
        if value is not None and not 10 <= len(value.get_secret_value()) <= 128:
            raise ValueError("Mật khẩu cần 10–128 ký tự")
        return value


class CreateAccount(ProfileFields):
    role: ManagedRole
    password: SecretStr
    organization_id: str | None = None


class UpdateAccount(ProfileFields):
    version: int = Field(ge=1)
    password: SecretStr | None = None


class DeleteAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = Field(ge=1)

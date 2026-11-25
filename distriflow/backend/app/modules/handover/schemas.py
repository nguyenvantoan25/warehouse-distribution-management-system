from pydantic import Field
from app.core.schemas import VersionedCommand


class ScanCommand(VersionedCommand):
    package_code: str = Field(min_length=1, max_length=80)

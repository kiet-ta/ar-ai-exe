from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class ExportPackageResponse(CamelModel):
    id: str
    design_id: str = Field(alias="designId")
    status: str
    download_url: str = Field(alias="downloadUrl")
    files: list[str]
    created_at: datetime = Field(alias="createdAt")

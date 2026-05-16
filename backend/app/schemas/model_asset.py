from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class ModelAssetResponse(CamelModel):
    id: str
    scan_session_id: str = Field(alias="scanSessionId")
    glb_url: str = Field(alias="glbUrl")
    obj_url: str = Field(alias="objUrl")
    mtl_url: str = Field(alias="mtlUrl")
    texture_url: str = Field(alias="textureUrl")
    quality_report_url: str = Field(alias="qualityReportUrl")
    quality_report: dict = Field(default_factory=dict, alias="qualityReport")
    created_at: datetime = Field(alias="createdAt")

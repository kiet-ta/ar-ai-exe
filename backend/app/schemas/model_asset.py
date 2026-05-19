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
    metadata_url: str = Field(alias="metadataUrl")
    quality_report_url: str = Field(alias="qualityReportUrl")
    obj_package_zip_url: str = Field(alias="objPackageZipUrl")
    quality_report: dict = Field(default_factory=dict, alias="qualityReport")
    created_at: datetime = Field(alias="createdAt")

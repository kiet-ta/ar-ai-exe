from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import ModelAsset, User
from app.schemas.model_asset import ModelAssetResponse
from app.services.file_helpers import read_json


class ModelAssetService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get(self, model_asset_id: str) -> ModelAsset:
        asset = self.db.get(ModelAsset, model_asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model asset not found.")
        return asset

    def get_for_user(self, model_asset_id: str, user: User) -> ModelAsset:
        asset = self.get(model_asset_id)
        if asset.scan_session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model asset not found.")
        return asset

    def file_path(self, asset: ModelAsset, file_type: str) -> Path:
        path_by_type = {
            "glb": asset.glb_path,
            "obj": asset.obj_path,
            "mtl": asset.mtl_path,
            "texture": asset.texture_path,
            "quality-report": asset.quality_report_path,
        }
        if file_type not in path_by_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported model file type.",
            )
        path = Path(path_by_type[file_type])
        if not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_type} file not found.")
        return path

    def response(self, asset: ModelAsset) -> ModelAssetResponse:
        report_path = Path(asset.quality_report_path)
        quality_report = read_json(report_path) if report_path.exists() else {}
        return ModelAssetResponse(
            id=asset.id,
            scanSessionId=asset.scan_session_id,
            glbUrl=f"/api/models/{asset.id}/download/glb",
            objUrl=f"/api/models/{asset.id}/download/obj",
            mtlUrl=f"/api/models/{asset.id}/download/mtl",
            textureUrl=f"/api/models/{asset.id}/download/texture",
            qualityReportUrl=f"/api/models/{asset.id}/quality-report",
            qualityReport=quality_report,
            createdAt=asset.created_at,
        )

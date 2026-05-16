from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import User
from app.schemas.model_asset import ModelAssetResponse
from app.services.file_helpers import read_json
from app.services.model_assets import ModelAssetService


router = APIRouter(prefix="/models", tags=["models"])


@router.get("/{model_asset_id}", response_model=ModelAssetResponse)
def get_model_asset(
    model_asset_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ModelAssetResponse:
    service = ModelAssetService(db)
    return service.response(service.get_for_user(model_asset_id, current_user))


@router.get("/{model_asset_id}/download/{file_type}")
def download_model_file(
    model_asset_id: str,
    file_type: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    service = ModelAssetService(db)
    asset = service.get_for_user(model_asset_id, current_user)
    path = service.file_path(asset, file_type)
    return FileResponse(path=path, filename=path.name)


@router.get("/{model_asset_id}/quality-report")
def get_quality_report(
    model_asset_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> JSONResponse:
    service = ModelAssetService(db)
    asset = service.get_for_user(model_asset_id, current_user)
    path = service.file_path(asset, "quality-report")
    return JSONResponse(content=read_json(path))

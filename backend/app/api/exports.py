from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models import User
from app.schemas.export import ExportPackageResponse
from app.services.export_packages import ExportPackageService


router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/{export_id}", response_model=ExportPackageResponse)
def get_export(
    export_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ExportPackageResponse:
    service = ExportPackageService(db)
    return service.response(service.get_for_user(export_id, current_user))


@router.get("/{export_id}/download")
def download_export(
    export_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FileResponse:
    export_package = ExportPackageService(db).get_for_user(export_id, current_user)
    return FileResponse(path=export_package.zip_path, filename=f"{export_package.id}.zip")

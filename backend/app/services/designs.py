from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Design, DesignStatus, ModelAsset, User
from app.schemas.design import DesignConfig, DesignResponse
from app.services.file_helpers import read_json, write_json


class DesignService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create(
        self,
        user: User,
        model_asset_id: str,
        name: str,
        config: DesignConfig | None,
    ) -> Design:
        asset = self.db.get(ModelAsset, model_asset_id)
        if not asset or asset.scan_session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model asset not found.")

        config_payload = (
            config.model_dump(by_alias=True)
            if config
            else DesignConfig(modelAssetId=model_asset_id).model_dump(by_alias=True)
        )
        design = Design(
            user_id=user.id,
            model_asset_id=model_asset_id,
            name=name,
            design_config_path="",
            status=DesignStatus.DRAFT,
        )
        self.db.add(design)
        self.db.flush()

        config_path = self._design_folder(design.id) / "design_config.json"
        write_json(config_path, config_payload)
        design.design_config_path = str(config_path)

        self.db.commit()
        self.db.refresh(design)
        return design

    def get_for_user(self, design_id: str, user: User) -> Design:
        design = self.db.get(Design, design_id)
        if not design or design.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found.")
        return design

    def update(
        self,
        design: Design,
        name: str | None = None,
        config: DesignConfig | None = None,
    ) -> Design:
        if name is not None:
            design.name = name
        if config is not None:
            write_json(Path(design.design_config_path), config.model_dump(by_alias=True))
        self.db.commit()
        self.db.refresh(design)
        return design

    def response(self, design: Design) -> DesignResponse:
        return DesignResponse(
            id=design.id,
            userId=design.user_id,
            modelAssetId=design.model_asset_id,
            name=design.name,
            status=design.status,
            designConfig=self.read_config(design),
            createdAt=design.created_at,
            updatedAt=design.updated_at,
        )

    def read_config(self, design: Design) -> dict[str, Any]:
        return read_json(Path(design.design_config_path))

    def _design_folder(self, design_id: str) -> Path:
        return self.settings.resolved_storage_root / "designs" / design_id

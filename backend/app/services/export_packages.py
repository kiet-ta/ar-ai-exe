import shutil
import zipfile
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Design, DesignStatus, ExportPackage, ModelAsset, User
from app.schemas.export import ExportPackageResponse
from app.services.file_helpers import read_json, write_json
from app.services.reconstruction import PLACEHOLDER_PNG


class ExportPackageService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create(self, design: Design) -> ExportPackage:
        asset = self.db.get(ModelAsset, design.model_asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model asset not found.")

        export_package = ExportPackage(
            design_id=design.id,
            glb_path="",
            obj_path="",
            mtl_path="",
            texture_path="",
            preview_images_path="",
            production_notes_path="",
            zip_path="",
        )
        self.db.add(export_package)
        self.db.flush()

        export_dir = self._export_folder(export_package.id)
        export_dir.mkdir(parents=True, exist_ok=True)

        glb_path = export_dir / "final_shoe.glb"
        obj_path = export_dir / "final_shoe.obj"
        mtl_path = export_dir / "final_shoe.mtl"
        texture_path = export_dir / "final_texture.png"
        design_config_path = export_dir / "design_config.json"
        measurement_info_path = export_dir / "measurement_info.json"
        production_notes_path = export_dir / "production_notes.json"
        preview_dir = export_dir

        shutil.copyfile(asset.glb_path, glb_path)
        shutil.copyfile(asset.obj_path, obj_path)
        shutil.copyfile(asset.mtl_path, mtl_path)
        shutil.copyfile(asset.texture_path, texture_path)
        shutil.copyfile(design.design_config_path, design_config_path)
        self._write_measurements(asset, measurement_info_path)
        self._write_previews(preview_dir)
        self._write_production_notes(design, production_notes_path)

        zip_path = export_dir / f"{export_package.id}.zip"
        self._zip_export(export_dir, zip_path)

        export_package.glb_path = str(glb_path)
        export_package.obj_path = str(obj_path)
        export_package.mtl_path = str(mtl_path)
        export_package.texture_path = str(texture_path)
        export_package.preview_images_path = str(preview_dir)
        export_package.production_notes_path = str(production_notes_path)
        export_package.zip_path = str(zip_path)
        design.status = DesignStatus.EXPORTED

        self.db.commit()
        self.db.refresh(export_package)
        return export_package

    def get(self, export_id: str) -> ExportPackage:
        export_package = self.db.get(ExportPackage, export_id)
        if not export_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export package not found.",
            )
        return export_package

    def get_for_user(self, export_id: str, user: User) -> ExportPackage:
        export_package = self.get(export_id)
        if export_package.design.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export package not found.",
            )
        return export_package

    def response(self, export_package: ExportPackage) -> ExportPackageResponse:
        return ExportPackageResponse(
            id=export_package.id,
            designId=export_package.design_id,
            status=export_package.status,
            downloadUrl=f"/api/exports/{export_package.id}/download",
            files=[
                "final_shoe.glb",
                "final_shoe.obj",
                "final_shoe.mtl",
                "final_texture.png",
                "preview_front.png",
                "preview_side.png",
                "preview_top.png",
                "preview_back.png",
                "design_config.json",
                "measurement_info.json",
                "production_notes.json",
            ],
            createdAt=export_package.created_at,
        )

    def _export_folder(self, export_id: str) -> Path:
        return self.settings.resolved_storage_root / "exports" / export_id

    def _write_measurements(self, asset: ModelAsset, path: Path) -> None:
        metadata_path = Path(asset.scan_session.metadata_path or "")
        metadata = read_json(metadata_path) if metadata_path.exists() else {}
        write_json(
            path,
            {
                "shoe": metadata.get("shoe", {}),
                "measurements": metadata.get("measurements", {}),
                "scanSetup": metadata.get("scanSetup", {}),
            },
        )

    def _write_previews(self, preview_dir: Path) -> None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        for name in ["front", "side", "top", "back"]:
            (preview_dir / f"preview_{name}.png").write_bytes(PLACEHOLDER_PNG)

    def _write_production_notes(self, design: Design, path: Path) -> None:
        metadata_path = Path(design.model_asset.scan_session.metadata_path or "")
        metadata = read_json(metadata_path) if metadata_path.exists() else {}
        design_config = read_json(Path(design.design_config_path))
        shoe = metadata.get("shoe", {})
        measurements = metadata.get("measurements", {})
        write_json(
            path,
            {
                "orderType": "visual_design_package",
                "shoe": {
                    "size": f"{shoe.get('sizeSystem', '')} {shoe.get('size', '')}".strip(),
                    "side": shoe.get("side"),
                    "lengthCm": measurements.get("lengthCm"),
                    "widthCm": measurements.get("widthCm"),
                    "material": shoe.get("material"),
                },
                "customization": {
                    "summary": self._summary(design_config),
                    "targetAreas": ["manual_reference"],
                    "colorCodes": [design_config.get("baseColor", "#ffffff")],
                    "notes": "Use preview images and design_config.json as manual customization reference.",
                },
                "files": [
                    "final_shoe.glb",
                    "final_shoe.obj",
                    "final_texture.png",
                    "preview_front.png",
                    "preview_side.png",
                    "preview_top.png",
                    "preview_back.png",
                ],
            },
        )

    def _summary(self, design_config: dict) -> str:
        sticker_count = len(design_config.get("stickers", []))
        text_count = len(design_config.get("texts", []))
        return (
            f"Shoe design with base color {design_config.get('baseColor', '#ffffff')}, "
            f"{sticker_count} sticker decal(s), and {text_count} text decal(s)."
        )

    def _zip_export(self, export_dir: Path, zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in export_dir.rglob("*"):
                if path == zip_path or path.is_dir():
                    continue
                archive.write(path, path.relative_to(export_dir))

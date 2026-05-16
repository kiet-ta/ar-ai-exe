from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import ModelAsset, ScanSession, ScanStatus, User
from app.schemas.scan import ScanMetadata
from app.services.file_helpers import write_json


class ScanSessionService:
    allowed_content_types = {"video/mp4"}
    allowed_extensions = {".mp4"}

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create(self, user: User, metadata: ScanMetadata | None = None) -> ScanSession:
        scan_session = ScanSession(user_id=user.id)
        self.db.add(scan_session)
        self.db.flush()

        if metadata:
            metadata_path = self._scan_folder(scan_session.id) / "metadata.json"
            write_json(metadata_path, metadata.model_dump(by_alias=True))
            scan_session.metadata_path = str(metadata_path)

        self.db.commit()
        self.db.refresh(scan_session)
        return scan_session

    def get_for_user(self, scan_session_id: str, user: User) -> ScanSession:
        scan_session = self.db.get(ScanSession, scan_session_id)
        if not scan_session or scan_session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan session not found.")
        return scan_session

    def get_model_asset_id(self, scan_session_id: str) -> str | None:
        asset = self.db.scalar(select(ModelAsset).where(ModelAsset.scan_session_id == scan_session_id))
        return asset.id if asset else None

    def save_upload(
        self,
        scan_session: ScanSession,
        file_name: str | None,
        content_type: str | None,
        video_bytes: bytes,
        metadata: ScanMetadata,
    ) -> ScanSession:
        self._validate_video(file_name, content_type, video_bytes)

        scan_folder = self._scan_folder(scan_session.id)
        video_path = scan_folder / "raw_video.mp4"
        metadata_path = scan_folder / "metadata.json"

        scan_folder.mkdir(parents=True, exist_ok=True)
        video_path.write_bytes(video_bytes)
        write_json(metadata_path, metadata.model_dump(by_alias=True))

        scan_session.raw_video_path = str(video_path)
        scan_session.metadata_path = str(metadata_path)
        scan_session.status = ScanStatus.UPLOADED
        scan_session.error_message = None
        self.db.commit()
        self.db.refresh(scan_session)
        return scan_session

    def set_status(
        self,
        scan_session_id: str,
        status_value: str,
        error_message: str | None = None,
    ) -> ScanSession:
        scan_session = self.db.get(ScanSession, scan_session_id)
        if not scan_session:
            raise ValueError(f"Scan session {scan_session_id} not found.")
        scan_session.status = status_value
        scan_session.error_message = error_message
        self.db.commit()
        self.db.refresh(scan_session)
        return scan_session

    def _scan_folder(self, scan_session_id: str) -> Path:
        return self.settings.resolved_storage_root / "raw-scans" / scan_session_id

    def _validate_video(
        self,
        file_name: str | None,
        content_type: str | None,
        video_bytes: bytes,
    ) -> None:
        suffix = Path(file_name or "").suffix.lower()
        if content_type not in self.allowed_content_types and suffix not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid video file. Upload an MP4 file using field name 'video'.",
            )

        if not video_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded video is empty.",
            )

        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        if len(video_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Uploaded video exceeds {self.settings.max_upload_size_mb} MB.",
            )

from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class ScanStatus:
    CREATED = "created"
    UPLOADED = "uploaded"
    EXTRACTING_FRAMES = "extracting_frames"
    RECONSTRUCTING = "reconstructing"
    CLEANING_MESH = "cleaning_mesh"
    UV_UNWRAPPING = "uv_unwrapping"
    TEXTURE_BAKING = "texture_baking"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"


class DesignStatus:
    DRAFT = "draft"
    EXPORTED = "exported"


class ExportStatus:
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("user"))
    role: Mapped[str] = mapped_column(String(32), default="demo_user")
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    scan_sessions: Mapped[list["ScanSession"]] = relationship(back_populates="user")
    designs: Mapped[list["Design"]] = relationship(back_populates="user")


class ScanSession(Base):
    __tablename__ = "scan_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("scan"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default=ScanStatus.CREATED, index=True)
    raw_video_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="scan_sessions")
    model_asset: Mapped["ModelAsset | None"] = relationship(
        back_populates="scan_session",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ModelAsset(Base):
    __tablename__ = "model_assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("model"))
    scan_session_id: Mapped[str] = mapped_column(
        ForeignKey("scan_sessions.id"),
        unique=True,
        index=True,
    )
    glb_path: Mapped[str] = mapped_column(Text)
    obj_path: Mapped[str] = mapped_column(Text)
    mtl_path: Mapped[str] = mapped_column(Text)
    texture_path: Mapped[str] = mapped_column(Text)
    quality_report_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    scan_session: Mapped[ScanSession] = relationship(back_populates="model_asset")
    designs: Mapped[list["Design"]] = relationship(back_populates="model_asset")


class Design(Base):
    __tablename__ = "designs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("design"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    model_asset_id: Mapped[str] = mapped_column(ForeignKey("model_assets.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    design_config_path: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default=DesignStatus.DRAFT, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="designs")
    model_asset: Mapped[ModelAsset] = relationship(back_populates="designs")
    export_packages: Mapped[list["ExportPackage"]] = relationship(back_populates="design")


class ExportPackage(Base):
    __tablename__ = "export_packages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("export"))
    design_id: Mapped[str] = mapped_column(ForeignKey("designs.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default=ExportStatus.COMPLETED)
    glb_path: Mapped[str] = mapped_column(Text)
    obj_path: Mapped[str] = mapped_column(Text)
    mtl_path: Mapped[str] = mapped_column(Text)
    texture_path: Mapped[str] = mapped_column(Text)
    preview_images_path: Mapped[str] = mapped_column(Text)
    production_notes_path: Mapped[str] = mapped_column(Text)
    zip_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    design: Mapped[Design] = relationship(back_populates="export_packages")

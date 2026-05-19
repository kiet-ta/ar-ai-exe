"""Add two-pass scan videos and package artifact metadata.

Revision ID: 20260519_0003
Revises: 20260517_0002
Create Date: 2026-05-19
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260519_0003"
down_revision: str | None = "20260517_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("scan_sessions", sa.Column("side_video_path", sa.Text(), nullable=True))
    op.add_column("scan_sessions", sa.Column("side_video_size_bytes", sa.Integer(), nullable=True))
    op.add_column(
        "scan_sessions",
        sa.Column("side_video_content_type", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "scan_sessions",
        sa.Column("side_video_checksum", sa.String(length=128), nullable=True),
    )
    op.add_column("scan_sessions", sa.Column("top_video_path", sa.Text(), nullable=True))
    op.add_column("scan_sessions", sa.Column("top_video_size_bytes", sa.Integer(), nullable=True))
    op.add_column(
        "scan_sessions",
        sa.Column("top_video_content_type", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "scan_sessions",
        sa.Column("top_video_checksum", sa.String(length=128), nullable=True),
    )

    op.add_column("model_assets", sa.Column("metadata_path", sa.Text(), nullable=True))
    op.add_column("model_assets", sa.Column("metadata_size_bytes", sa.Integer(), nullable=True))
    op.add_column(
        "model_assets",
        sa.Column("metadata_content_type", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "model_assets",
        sa.Column("metadata_checksum", sa.String(length=128), nullable=True),
    )
    op.add_column("model_assets", sa.Column("obj_package_zip_path", sa.Text(), nullable=True))
    op.add_column(
        "model_assets",
        sa.Column("obj_package_zip_size_bytes", sa.Integer(), nullable=True),
    )
    op.add_column(
        "model_assets",
        sa.Column("obj_package_zip_content_type", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "model_assets",
        sa.Column("obj_package_zip_checksum", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("model_assets", "obj_package_zip_checksum")
    op.drop_column("model_assets", "obj_package_zip_content_type")
    op.drop_column("model_assets", "obj_package_zip_size_bytes")
    op.drop_column("model_assets", "obj_package_zip_path")
    op.drop_column("model_assets", "metadata_checksum")
    op.drop_column("model_assets", "metadata_content_type")
    op.drop_column("model_assets", "metadata_size_bytes")
    op.drop_column("model_assets", "metadata_path")

    op.drop_column("scan_sessions", "top_video_checksum")
    op.drop_column("scan_sessions", "top_video_content_type")
    op.drop_column("scan_sessions", "top_video_size_bytes")
    op.drop_column("scan_sessions", "top_video_path")
    op.drop_column("scan_sessions", "side_video_checksum")
    op.drop_column("scan_sessions", "side_video_content_type")
    op.drop_column("scan_sessions", "side_video_size_bytes")
    op.drop_column("scan_sessions", "side_video_path")

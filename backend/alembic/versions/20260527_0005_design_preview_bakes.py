"""Add baked preview metadata to designs.

Revision ID: 20260527_0005
Revises: 20260523_0004
Create Date: 2026-05-27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260527_0005"
down_revision: str | None = "20260523_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("designs", sa.Column("preview_glb_path", sa.Text(), nullable=True))
    op.add_column("designs", sa.Column("preview_glb_size_bytes", sa.Integer(), nullable=True))
    op.add_column("designs", sa.Column("preview_glb_content_type", sa.String(length=120), nullable=True))
    op.add_column("designs", sa.Column("preview_glb_checksum", sa.String(length=128), nullable=True))
    op.add_column(
        "designs",
        sa.Column("preview_status", sa.String(length=32), nullable=False, server_default="none"),
    )
    op.add_column("designs", sa.Column("preview_error_message", sa.Text(), nullable=True))
    op.add_column("designs", sa.Column("preview_updated_at", sa.DateTime(), nullable=True))
    op.create_index("ix_designs_preview_status", "designs", ["preview_status"])


def downgrade() -> None:
    op.drop_index("ix_designs_preview_status", table_name="designs")
    op.drop_column("designs", "preview_updated_at")
    op.drop_column("designs", "preview_error_message")
    op.drop_column("designs", "preview_status")
    op.drop_column("designs", "preview_glb_checksum")
    op.drop_column("designs", "preview_glb_content_type")
    op.drop_column("designs", "preview_glb_size_bytes")
    op.drop_column("designs", "preview_glb_path")

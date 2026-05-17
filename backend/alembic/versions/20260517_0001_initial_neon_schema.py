"""Initial Shoe Visual Customizer schema.

Revision ID: 20260517_0001
Revises:
Create Date: 2026-05-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260517_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "scan_sessions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("raw_video_path", sa.Text(), nullable=True),
        sa.Column("metadata_path", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scan_sessions_status", "scan_sessions", ["status"])
    op.create_index("ix_scan_sessions_user_id", "scan_sessions", ["user_id"])

    op.create_table(
        "model_assets",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("scan_session_id", sa.String(length=64), nullable=False),
        sa.Column("glb_path", sa.Text(), nullable=False),
        sa.Column("obj_path", sa.Text(), nullable=False),
        sa.Column("mtl_path", sa.Text(), nullable=False),
        sa.Column("texture_path", sa.Text(), nullable=False),
        sa.Column("quality_report_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scan_session_id"], ["scan_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_model_assets_scan_session_id",
        "model_assets",
        ["scan_session_id"],
        unique=True,
    )

    op.create_table(
        "designs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("model_asset_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("design_config_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["model_asset_id"], ["model_assets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_designs_model_asset_id", "designs", ["model_asset_id"])
    op.create_index("ix_designs_status", "designs", ["status"])
    op.create_index("ix_designs_user_id", "designs", ["user_id"])

    op.create_table(
        "export_packages",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("design_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("glb_path", sa.Text(), nullable=False),
        sa.Column("obj_path", sa.Text(), nullable=False),
        sa.Column("mtl_path", sa.Text(), nullable=False),
        sa.Column("texture_path", sa.Text(), nullable=False),
        sa.Column("preview_images_path", sa.Text(), nullable=False),
        sa.Column("production_notes_path", sa.Text(), nullable=False),
        sa.Column("zip_path", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["design_id"], ["designs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_export_packages_design_id", "export_packages", ["design_id"])


def downgrade() -> None:
    op.drop_index("ix_export_packages_design_id", table_name="export_packages")
    op.drop_table("export_packages")

    op.drop_index("ix_designs_user_id", table_name="designs")
    op.drop_index("ix_designs_status", table_name="designs")
    op.drop_index("ix_designs_model_asset_id", table_name="designs")
    op.drop_table("designs")

    op.drop_index("ix_model_assets_scan_session_id", table_name="model_assets")
    op.drop_table("model_assets")

    op.drop_index("ix_scan_sessions_user_id", table_name="scan_sessions")
    op.drop_index("ix_scan_sessions_status", table_name="scan_sessions")
    op.drop_table("scan_sessions")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

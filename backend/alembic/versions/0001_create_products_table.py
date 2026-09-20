"""create products table

Revision ID: 0001_create_products_table
Revises:
Create Date: 2026-09-20 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_create_products_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("current_stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("lead_time", sa.Integer(), server_default="0", nullable=False),
        sa.Column("supplier", sa.String(length=255), nullable=True),
        sa.Column("reorder_point", sa.Integer(), server_default="0", nullable=False),
        sa.Column("safety_stock", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("current_stock >= 0", name="ck_products_current_stock_non_negative"),
        sa.CheckConstraint("unit_cost >= 0", name="ck_products_unit_cost_non_negative"),
        sa.CheckConstraint("lead_time >= 0", name="ck_products_lead_time_non_negative"),
        sa.CheckConstraint("reorder_point >= 0", name="ck_products_reorder_point_non_negative"),
        sa.CheckConstraint("safety_stock >= 0", name="ck_products_safety_stock_non_negative"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
    )


def downgrade() -> None:
    op.drop_table("products")
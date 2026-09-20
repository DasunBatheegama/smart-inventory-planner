"""create sales tables

Revision ID: 0002_create_sales_tables
Revises: 0001_create_products_table
Create Date: 2026-09-20 00:00:00.000001
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_create_sales_tables"
down_revision = "0001_create_products_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_uploads",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("total_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("valid_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("invalid_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("imported_rows", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    op.create_table(
        "sales_records",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("quantity_sold", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("quantity_sold >= 0", name="ck_sales_records_quantity_sold_non_negative"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("ix_sales_records_product_id", "sales_records", ["product_id"])
    op.create_index("ix_sales_records_date", "sales_records", ["date"])


def downgrade() -> None:
    op.drop_index("ix_sales_records_date", table_name="sales_records")
    op.drop_index("ix_sales_records_product_id", table_name="sales_records")
    op.drop_table("sales_records")
    op.drop_table("sales_uploads")
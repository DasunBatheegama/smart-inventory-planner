"""create forecasts table

Revision ID: 0003_create_forecasts_table
Revises: 0002_create_sales_tables
Create Date: 2026-09-20 00:00:02.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_create_forecasts_table"
down_revision = "0002_create_sales_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "forecasts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("forecast_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("forecast_quantity >= 0", name="ck_forecasts_forecast_quantity_non_negative"),
        sa.CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 100)", name="ck_forecasts_confidence_percent_range"),
        sa.CheckConstraint("method IN ('moving_average', 'exponential_smoothing')", name="ck_forecasts_method_valid"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
    )
    op.create_index("ix_forecasts_product_id", "forecasts", ["product_id"])
    op.create_index("ix_forecasts_forecast_date", "forecasts", ["forecast_date"])


def downgrade() -> None:
    op.drop_index("ix_forecasts_forecast_date", table_name="forecasts")
    op.drop_index("ix_forecasts_product_id", table_name="forecasts")
    op.drop_table("forecasts")
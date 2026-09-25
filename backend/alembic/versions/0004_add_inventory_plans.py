"""add inventory_plans table

Revision ID: 0004_add_inventory_plans
Revises: 0003_create_forecasts_table
Create Date: 2026-09-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_add_inventory_plans"
down_revision = "0003_create_forecasts_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("forecast_id", sa.String(length=36), sa.ForeignKey("forecasts.id"), nullable=True),
        sa.Column("current_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_daily_demand", sa.Numeric(14, 4), nullable=True),
        sa.Column("forecast_demand", sa.Numeric(14, 4), nullable=True),
        sa.Column("safety_stock", sa.Integer(), nullable=True),
        sa.Column("reorder_point", sa.Integer(), nullable=True),
        sa.Column("eoq", sa.Numeric(14, 4), nullable=True),
        sa.Column("recommended_order_quantity", sa.Integer(), nullable=True),
        sa.Column("days_of_inventory", sa.Numeric(14, 4), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="healthy"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_inventory_plans_product_id", "inventory_plans", ["product_id"], unique=False)
    op.create_index("ix_inventory_plans_forecast_id", "inventory_plans", ["forecast_id"], unique=False)
    op.create_index("ix_inventory_plans_status", "inventory_plans", ["status"], unique=False)
    op.create_index("ix_inventory_plans_created_at", "inventory_plans", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_inventory_plans_created_at", table_name="inventory_plans")
    op.drop_index("ix_inventory_plans_status", table_name="inventory_plans")
    op.drop_index("ix_inventory_plans_forecast_id", table_name="inventory_plans")
    op.drop_index("ix_inventory_plans_product_id", table_name="inventory_plans")
    op.drop_table("inventory_plans")

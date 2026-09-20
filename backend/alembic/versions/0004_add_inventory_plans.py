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
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False, index=True),
        sa.Column("forecast_id", sa.String(length=36), sa.ForeignKey("forecasts.id"), nullable=True, index=True),
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
    # Indexes are created implicitly for some DBs when columns are declared with index=True.
    # Create explicit indexes only where necessary; SQLite may already create them.
    try:
        op.create_index(op.f("ix_inventory_plans_product_id"), "inventory_plans", ["product_id"], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f("ix_inventory_plans_status"), "inventory_plans", ["status"], unique=False)
    except Exception:
        pass
    try:
        op.create_index(op.f("ix_inventory_plans_created_at"), "inventory_plans", ["created_at"], unique=False)
    except Exception:
        pass


def downgrade() -> None:
    # best-effort drops
    for idx in ("ix_inventory_plans_created_at", "ix_inventory_plans_status", "ix_inventory_plans_product_id"):
        try:
            op.drop_index(op.f(idx), table_name="inventory_plans")
        except Exception:
            pass
    op.drop_table("inventory_plans")

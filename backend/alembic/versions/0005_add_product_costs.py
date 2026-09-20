"""add ordering and holding cost to products

Revision ID: 0005_add_product_costs
Revises: 0004_add_inventory_plans
Create Date: 2026-09-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_add_product_costs"
down_revision = "0004_add_inventory_plans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("ordering_cost", sa.Numeric(12, 2), nullable=True))
    op.add_column("products", sa.Column("holding_cost_per_unit", sa.Numeric(12, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "holding_cost_per_unit")
    op.drop_column("products", "ordering_cost")

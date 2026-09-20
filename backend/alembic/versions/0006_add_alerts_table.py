"""add alerts table

Revision ID: 0006_add_alerts_table
Revises: 0005_add_product_costs
Create Date: 2026-09-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006_add_alerts_table"
down_revision = "0005_add_product_costs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    alert_type = sa.Enum(
        "low_stock",
        "stockout_risk",
        "reorder_required",
        "overstock",
        "slow_moving",
        "forecast_anomaly",
        name="alert_type",
        native_enum=False,
        create_constraint=True,
    )
    alert_severity = sa.Enum(
        "critical",
        "warning",
        "info",
        name="alert_severity",
        native_enum=False,
        create_constraint=True,
    )
    alert_status = sa.Enum(
        "new",
        "acknowledged",
        "resolved",
        name="alert_status",
        native_enum=False,
        create_constraint=True,
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("type", alert_type, nullable=False),
        sa.Column("severity", alert_severity, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.String(length=2000), nullable=False),
        sa.Column("recommendation", sa.String(length=2000), nullable=False),
        sa.Column("status", alert_status, nullable=False, server_default="new"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_product_id", "alerts", ["product_id"], unique=False)
    op.create_index("ix_alerts_type", "alerts", ["type"], unique=False)
    op.create_index("ix_alerts_severity", "alerts", ["severity"], unique=False)
    op.create_index("ix_alerts_status", "alerts", ["status"], unique=False)
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_alerts_created_at", table_name="alerts")
    op.drop_index("ix_alerts_status", table_name="alerts")
    op.drop_index("ix_alerts_severity", table_name="alerts")
    op.drop_index("ix_alerts_type", table_name="alerts")
    op.drop_index("ix_alerts_product_id", table_name="alerts")
    op.drop_table("alerts")
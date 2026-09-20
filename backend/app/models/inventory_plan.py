from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class InventoryPlan(Base):
    __tablename__ = "inventory_plans"
    __table_args__ = (
        CheckConstraint("current_stock >= 0", name="ck_inventory_plans_current_stock_non_negative"),
        CheckConstraint("average_daily_demand >= 0", name="ck_inventory_plans_avg_daily_demand_non_negative"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    forecast_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("forecasts.id"), nullable=True, index=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    average_daily_demand: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    forecast_demand: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    safety_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reorder_point: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eoq: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    recommended_order_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_of_inventory: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy", server_default="healthy", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    product = relationship("Product")
    forecast = relationship("Forecast")

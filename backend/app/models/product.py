from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Product(Base):
    """Inventory product persisted in PostgreSQL."""

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("current_stock >= 0", name="ck_products_current_stock_non_negative"),
        CheckConstraint("unit_cost >= 0", name="ck_products_unit_cost_non_negative"),
        CheckConstraint("lead_time >= 0", name="ck_products_lead_time_non_negative"),
        CheckConstraint("reorder_point >= 0", name="ck_products_reorder_point_non_negative"),
        CheckConstraint("safety_stock >= 0", name="ck_products_safety_stock_non_negative"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0, server_default="0")
    lead_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ordering_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True, default=None
    )
    holding_cost_per_unit: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True, default=None
    )
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    sales_records = relationship("SalesRecord", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product", cascade="all, delete-orphan")

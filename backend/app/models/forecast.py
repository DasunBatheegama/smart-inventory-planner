from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        CheckConstraint("forecast_quantity >= 0", name="ck_forecasts_forecast_quantity_non_negative"),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 100)",
            name="ck_forecasts_confidence_percent_range",
        ),
        CheckConstraint(
            "method IN ('moving_average', 'exponential_smoothing')",
            name="ck_forecasts_method_valid",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    forecast_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    product = relationship("Product", back_populates="forecasts")
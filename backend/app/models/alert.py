from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AlertType(str, Enum):
    low_stock = "low_stock"
    stockout_risk = "stockout_risk"
    reorder_required = "reorder_required"
    overstock = "overstock"
    slow_moving = "slow_moving"
    forecast_anomaly = "forecast_anomaly"


class AlertSeverity(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"


class AlertStatus(str, Enum):
    new = "new"
    acknowledged = "acknowledged"
    resolved = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    type: Mapped[AlertType] = mapped_column(
        SAEnum(AlertType, name="alert_type", native_enum=False, create_constraint=True),
        nullable=False,
        index=True,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        SAEnum(AlertSeverity, name="alert_severity", native_enum=False, create_constraint=True),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(2000), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        SAEnum(AlertStatus, name="alert_status", native_enum=False, create_constraint=True),
        nullable=False,
        default=AlertStatus.new,
        server_default=AlertStatus.new.value,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="alerts")
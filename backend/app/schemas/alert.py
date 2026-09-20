from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertSeverity, AlertStatus, AlertType


class AlertProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    name: str
    category: Optional[str] = None
    supplier: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    product: Optional[AlertProductSummary] = None
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recommendation: str
    status: AlertStatus
    created_at: datetime
    updated_at: datetime


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AlertGenerateResponse(BaseModel):
    generated: int
    skipped_duplicates: int
    message: str


class AlertUpdateRequest(BaseModel):
    status: AlertStatus


class AlertSummaryResponse(BaseModel):
    total_active: int
    critical: int
    warning: int
    info: int
    reorder_required: int
    low_stock: int
    stockout_risk: int
    overstock: int
    slow_moving: int
    forecast_anomaly: int
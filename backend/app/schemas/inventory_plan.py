from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class InventoryPlanResponse(BaseModel):
    id: str
    product_id: str
    forecast_id: Optional[str] = None
    current_stock: int
    average_daily_demand: Optional[Decimal] = None
    forecast_demand: Optional[Decimal] = None
    safety_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    eoq: Optional[Decimal] = None
    recommended_order_quantity: Optional[int] = None
    days_of_inventory: Optional[Decimal] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InventoryPlanGenerateRequest(BaseModel):
    product_id: str
    forecast_id: Optional[str] = None
    service_level: float = Field(default=0.95, ge=0.0, le=1.0)
    review_period: int = Field(default=30, ge=0)
    lead_time: Optional[int] = None


class InventoryPlanSummaryResponse(BaseModel):
    total_inventory_value: float
    products_requiring_reorder: int
    critical_products: int
    healthy_products: int
    average_days_of_inventory: Optional[float]

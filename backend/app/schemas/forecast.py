from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ForecastGenerateRequest(BaseModel):
    product_id: str = Field(min_length=1)
    method: str = Field(min_length=1)
    forecast_horizon: int = Field(description="Forecast horizon in months. Allowed values: 1, 3, 6, 12.")


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    forecast_date: date
    forecast_quantity: float
    method: str
    confidence: Optional[float] = None
    created_at: datetime


class ForecastSummaryResponse(BaseModel):
    product_id: str
    average_daily_demand: float
    forecast_demand: float
    growth_percentage: float
    method: str
    forecast_horizon: int
    confidence: Optional[float] = None
    accuracy: Optional[dict[str, float]] = None
    accuracy_reason: Optional[str] = None
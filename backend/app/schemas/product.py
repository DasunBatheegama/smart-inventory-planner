from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


NonNegativeInt = Annotated[int, Field(ge=0)]
NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]


class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    category: Optional[str] = Field(default=None, max_length=255)
    current_stock: NonNegativeInt = 0
    unit_cost: NonNegativeDecimal = Decimal("0")
    lead_time: NonNegativeInt = 0
    supplier: Optional[str] = Field(default=None, max_length=255)
    reorder_point: NonNegativeInt = 0
    safety_stock: NonNegativeInt = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, min_length=1, max_length=100)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    category: Optional[str] = Field(default=None, max_length=255)
    current_stock: Optional[NonNegativeInt] = None
    unit_cost: Optional[NonNegativeDecimal] = None
    lead_time: Optional[NonNegativeInt] = None
    supplier: Optional[str] = Field(default=None, max_length=255)
    reorder_point: Optional[NonNegativeInt] = None
    safety_stock: Optional[NonNegativeInt] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    name: str
    category: Optional[str] = None
    current_stock: int
    unit_cost: float
    lead_time: int
    supplier: Optional[str] = None
    reorder_point: int
    safety_stock: int
    status: str
    inventory_value: float
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductStatsResponse(BaseModel):
    total_products: int
    total_inventory_value: float
    low_stock_products: int
    out_of_stock_products: int
    average_stock_level: float
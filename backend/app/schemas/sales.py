from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SalesRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    sku: str
    product_name: str
    date: date
    quantity_sold: int
    created_at: datetime


class SalesUploadError(BaseModel):
    row: int
    error: str


class SalesUploadResponse(BaseModel):
    file_name: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    imported_rows: int
    status: Literal["processing", "completed", "failed", "completed_with_errors"]
    errors: list[SalesUploadError] = Field(default_factory=list)


class SalesSummaryResponse(BaseModel):
    total_sales_records: int
    total_units_sold: int
    products_with_sales: int
    first_sales_date: date | None
    latest_sales_date: date | None
    last_upload_date: datetime | None


class SalesListResponse(BaseModel):
    items: list[SalesRecordResponse]
    total: int
    page: int
    page_size: int


class SalesUploadHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_name: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    imported_rows: int
    status: Literal["processing", "completed", "failed", "completed_with_errors"]
    created_at: datetime


class SalesUploadHistoryListResponse(BaseModel):
    items: list[SalesUploadHistoryResponse]
    total: int
    page: int
    page_size: int
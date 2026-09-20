from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.sales import (
    SalesListResponse,
    SalesRecordResponse,
    SalesSummaryResponse,
    SalesUploadHistoryListResponse,
    SalesUploadResponse,
)
from app.services.sales import SalesFileError, get_sales_record, get_sales_summary, get_sales_upload_history, import_sales_csv, list_sales_records

router = APIRouter(tags=["Sales"])


@router.post("/sales/upload", response_model=SalesUploadResponse)
def upload_sales(file: UploadFile = File(...), db: Session = Depends(get_db)) -> SalesUploadResponse:
    try:
        return import_sales_csv(db, file)
    except SalesFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/sales", response_model=SalesListResponse)
def read_sales(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sku: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> SalesListResponse:
    return list_sales_records(db, page=page, page_size=page_size, sku=sku, start_date=start_date, end_date=end_date)


@router.get("/sales/summary", response_model=SalesSummaryResponse)
def read_sales_summary(db: Session = Depends(get_db)) -> SalesSummaryResponse:
    return get_sales_summary(db)


@router.get("/sales/uploads", response_model=SalesUploadHistoryListResponse)
def read_sales_uploads(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SalesUploadHistoryListResponse:
    return get_sales_upload_history(db, page=page, page_size=page_size)


@router.get("/sales/{sales_id}", response_model=SalesRecordResponse)
def read_sales_record(sales_id: str, db: Session = Depends(get_db)) -> SalesRecordResponse:
    record = get_sales_record(db, sales_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales record not found.")
    return record
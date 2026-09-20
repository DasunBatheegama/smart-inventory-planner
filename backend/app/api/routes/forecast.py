from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.forecast import ForecastGenerateRequest, ForecastResponse, ForecastSummaryResponse
from app.services.forecast import (
    ForecastCalculationError,
    ForecastHistoryNotFoundError,
    ForecastProductNotFoundError,
    ForecastingError,
    InsufficientHistoricalDataError,
    InvalidForecastHorizonError,
    InvalidForecastMethodError,
    generate_forecast,
    get_forecast_summary,
    get_forecasts_by_product,
    list_forecasts,
)

router = APIRouter(tags=["Forecasts"])


def _map_forecast_error(exc: ForecastingError) -> HTTPException:
    if isinstance(exc, ForecastProductNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ForecastHistoryNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (InsufficientHistoricalDataError, InvalidForecastMethodError, InvalidForecastHorizonError, ForecastCalculationError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Forecast generation failed.")


@router.post("/forecasts/generate", response_model=list[ForecastResponse], status_code=status.HTTP_201_CREATED)
def generate_forecast_endpoint(payload: ForecastGenerateRequest, db: Session = Depends(get_db)) -> list[ForecastResponse]:
    try:
        return generate_forecast(db, payload)
    except ForecastingError as exc:
        raise _map_forecast_error(exc) from exc


@router.get("/forecasts", response_model=list[ForecastResponse])
def read_forecasts(
    product_id: str | None = Query(default=None),
    method: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ForecastResponse]:
    try:
        return list_forecasts(db, product_id=product_id, method=method, start_date=start_date, end_date=end_date)
    except ForecastingError as exc:
        raise _map_forecast_error(exc) from exc


@router.get("/forecasts/{product_id}/summary", response_model=ForecastSummaryResponse)
def read_forecast_summary(product_id: str, db: Session = Depends(get_db)) -> ForecastSummaryResponse:
    try:
        return get_forecast_summary(db, product_id)
    except ForecastingError as exc:
        raise _map_forecast_error(exc) from exc


@router.get("/forecasts/{product_id}", response_model=list[ForecastResponse])
def read_forecasts_for_product(
    product_id: str,
    method: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ForecastResponse]:
    try:
        return get_forecasts_by_product(db, product_id, method=method, start_date=start_date, end_date=end_date)
    except ForecastingError as exc:
        raise _map_forecast_error(exc) from exc
from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories import forecast as forecast_repository
from app.repositories import product as product_repository
from app.services.forecast import (
    ForecastHistoryNotFoundError,
    ForecastProductNotFoundError,
    get_forecast_summary as service_get_forecast_summary,
    get_forecasts_by_product,
    list_forecasts,
)


class ForecastToolError(Exception):
    """Base error for forecast agent tools."""


class ForecastToolProductNotFoundError(ForecastToolError):
    """Raised when a tool is asked about a product that does not exist."""


MAX_FORECAST_ROWS = 50


def _forecast_to_dict(forecast) -> dict[str, object]:
    return {
        "id": forecast.id,
        "product_id": forecast.product_id,
        "forecast_date": forecast.forecast_date.isoformat(),
        "forecast_quantity": float(forecast.forecast_quantity),
        "method": forecast.method,
        "confidence": float(forecast.confidence) if forecast.confidence is not None else None,
        "created_at": forecast.created_at.isoformat(),
    }


def _product_not_found_or_raise(exc: Exception) -> None:
    if isinstance(exc, ForecastProductNotFoundError):
        raise ForecastToolProductNotFoundError(str(exc)) from exc


def get_product_forecast(db: Session, product_id: str) -> list[dict[str, object]]:
    try:
        forecasts = get_forecasts_by_product(db, product_id)
    except ForecastProductNotFoundError as exc:
        raise ForecastToolProductNotFoundError(str(exc)) from exc
    return [_forecast_to_dict(forecast) for forecast in forecasts]


def get_forecast_summary(db: Session, product_id: str) -> dict[str, object] | None:
    try:
        summary = service_get_forecast_summary(db, product_id)
    except ForecastProductNotFoundError as exc:
        raise ForecastToolProductNotFoundError(str(exc)) from exc
    except ForecastHistoryNotFoundError:
        return None
    return summary.model_dump(mode="json")


def get_forecast_accuracy(db: Session, product_id: str) -> dict[str, object] | None:
    try:
        summary = service_get_forecast_summary(db, product_id)
    except ForecastProductNotFoundError as exc:
        raise ForecastToolProductNotFoundError(str(exc)) from exc
    except ForecastHistoryNotFoundError:
        return None
    return summary.accuracy


def get_forecasts(
    db: Session,
    filters: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    filters = filters or {}
    product_id = filters.get("product_id")
    if product_id is not None and product_repository.get_product_by_id(db, product_id) is None:
        raise ForecastToolProductNotFoundError("Product not found.")
    try:
        forecasts = list_forecasts(
            db,
            product_id=product_id,
            method=filters.get("method"),
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
        )
    except ForecastProductNotFoundError as exc:
        raise ForecastToolProductNotFoundError(str(exc)) from exc
    return [_forecast_to_dict(forecast) for forecast in forecasts[:MAX_FORECAST_ROWS]]


def compare_forecast_periods(db: Session, product_id: str) -> dict[str, object] | None:
    if product_repository.get_product_by_id(db, product_id) is None:
        raise ForecastToolProductNotFoundError("Product not found.")

    batch = forecast_repository.get_latest_forecast_batch(db, product_id=product_id)
    if len(batch) < 2:
        return None

    latest = batch[-1]
    previous = batch[-2]
    latest_quantity = float(latest.forecast_quantity)
    previous_quantity = float(previous.forecast_quantity)
    absolute_change = latest_quantity - previous_quantity
    percent_change = (absolute_change / previous_quantity * 100) if previous_quantity else None

    return {
        "latest_period": latest.forecast_date.isoformat(),
        "previous_period": previous.forecast_date.isoformat(),
        "latest_quantity": round(latest_quantity, 4),
        "previous_quantity": round(previous_quantity, 4),
        "absolute_change": round(absolute_change, 4),
        "percent_change": round(percent_change, 2) if percent_change is not None else None,
    }
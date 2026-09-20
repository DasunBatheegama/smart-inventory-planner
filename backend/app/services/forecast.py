from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.forecast import Forecast
from app.repositories import forecast as forecast_repository
from app.repositories import product as product_repository
from app.schemas.forecast import ForecastGenerateRequest, ForecastResponse, ForecastSummaryResponse
from app.services.forecasting import forecast_daily_exponential_smoothing, forecast_daily_moving_average


SUPPORTED_METHODS = {"moving_average", "exponential_smoothing"}
SUPPORTED_HORIZONS = {1, 3, 6, 12}
MIN_HISTORY_DAYS = 30
MIN_ACCURACY_HISTORY_DAYS = 60


class ForecastingError(Exception):
    pass


class ForecastProductNotFoundError(ForecastingError):
    pass


class ForecastHistoryNotFoundError(ForecastingError):
    pass


class InsufficientHistoricalDataError(ForecastingError):
    pass


class InvalidForecastMethodError(ForecastingError):
    pass


class InvalidForecastHorizonError(ForecastingError):
    pass


class ForecastCalculationError(ForecastingError):
    pass


def _month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _next_month_start(value: date) -> date:
    return _add_months(_month_start(value), 1)


def _count_days_in_months(start_date: date, months: int) -> int:
    current = start_date
    total = 0
    for _ in range(months):
        total += monthrange(current.year, current.month)[1]
        current = _add_months(current, 1)
    return total


def _group_sales_by_day(records) -> list[tuple[date, int]]:
    if not records:
        return []

    aggregated: dict[date, int] = defaultdict(int)
    for record in records:
        aggregated[record.date] += int(record.quantity_sold)

    first_date = min(aggregated)
    last_date = max(aggregated)
    current = first_date
    series: list[tuple[date, int]] = []
    while current <= last_date:
        series.append((current, aggregated.get(current, 0)))
        current += timedelta(days=1)
    return series


def _validate_history(series: list[tuple[date, int]]) -> None:
    if not series:
        raise ForecastHistoryNotFoundError("No sales history exists for this product.")

    covered_days = (series[-1][0] - series[0][0]).days + 1
    if covered_days < MIN_HISTORY_DAYS:
        raise InsufficientHistoricalDataError("Insufficient historical sales data. At least 30 days are required.")


def _prepare_daily_history(records) -> list[tuple[date, int]]:
    series = _group_sales_by_day(records)
    _validate_history(series)
    return series


def _forecast_daily_values(method: str, history_values: list[int], forecast_start: date, forecast_days: int) -> list[tuple[date, float]]:
    try:
        if method == "moving_average":
            return forecast_daily_moving_average([float(value) for value in history_values], forecast_start, forecast_days)
        if method == "exponential_smoothing":
            return forecast_daily_exponential_smoothing([float(value) for value in history_values], forecast_start, forecast_days)
    except Exception as exc:  # pragma: no cover - defensive conversion
        raise ForecastCalculationError("Forecast calculation failure.") from exc

    raise InvalidForecastMethodError("Invalid forecasting method.")


def _aggregate_daily_predictions_to_months(daily_predictions: list[tuple[date, float]]) -> list[tuple[date, float]]:
    monthly_totals: dict[date, float] = defaultdict(float)
    for forecast_day, quantity in daily_predictions:
        monthly_totals[_month_start(forecast_day)] += float(quantity)
    return sorted(monthly_totals.items(), key=lambda item: item[0])


def _validate_request(payload: ForecastGenerateRequest) -> None:
    if payload.method not in SUPPORTED_METHODS:
        raise InvalidForecastMethodError("Invalid forecasting method.")
    if payload.forecast_horizon not in SUPPORTED_HORIZONS:
        raise InvalidForecastHorizonError("Invalid forecast horizon.")


def _to_response(forecast: Forecast) -> ForecastResponse:
    return ForecastResponse.model_validate(
        {
            "id": forecast.id,
            "product_id": forecast.product_id,
            "forecast_date": forecast.forecast_date,
            "forecast_quantity": float(forecast.forecast_quantity),
            "method": forecast.method,
            "confidence": float(forecast.confidence) if forecast.confidence is not None else None,
            "created_at": forecast.created_at,
        }
    )


def calculate_forecast_accuracy(method: str, history_values: list[int]) -> dict[str, float] | None:
    if len(history_values) < MIN_ACCURACY_HISTORY_DAYS:
        return None

    validation_days = min(14, max(7, len(history_values) // 5))
    if len(history_values) <= validation_days:
        return None

    train_values = history_values[:-validation_days]
    validation_values = history_values[-validation_days:]
    forecast_start = date(2000, 1, 1)
    predictions = _forecast_daily_values(method, train_values, forecast_start, validation_days)
    predicted_values = [value for _, value in predictions]
    if not predicted_values:
        return None

    abs_errors = [abs(actual - predicted) for actual, predicted in zip(validation_values, predicted_values)]
    mae = sum(abs_errors) / len(abs_errors)
    non_zero_pairs = [(actual, predicted) for actual, predicted in zip(validation_values, predicted_values) if actual != 0]
    if non_zero_pairs:
        mape = sum(abs((actual - predicted) / actual) for actual, predicted in non_zero_pairs) / len(non_zero_pairs) * 100
    else:
        mape = 0.0
    return {"mae": float(mae), "mape": float(mape)}


def generate_forecast(db: Session, payload: ForecastGenerateRequest) -> list[ForecastResponse]:
    _validate_request(payload)

    product = product_repository.get_product_by_id(db, payload.product_id)
    if product is None:
        raise ForecastProductNotFoundError("Product not found.")

    sales_records = forecast_repository.get_sales_history(db, payload.product_id)
    daily_history = _prepare_daily_history(sales_records)
    history_values = [quantity for _, quantity in daily_history]
    forecast_start = _next_month_start(daily_history[-1][0])
    forecast_days = _count_days_in_months(forecast_start, payload.forecast_horizon)
    daily_predictions = _forecast_daily_values(payload.method, history_values, forecast_start, forecast_days)
    monthly_predictions = _aggregate_daily_predictions_to_months(daily_predictions)
    accuracy = calculate_forecast_accuracy(payload.method, history_values)
    confidence = None
    if accuracy is not None:
        confidence = max(0.0, min(100.0, 100.0 - accuracy["mape"]))

    batch_created_at = datetime.now(timezone.utc)
    forecasts = [
        Forecast(
            product_id=payload.product_id,
            forecast_date=forecast_date,
            forecast_quantity=Decimal(str(quantity)),
            method=payload.method,
            confidence=Decimal(str(confidence)) if confidence is not None else None,
            created_at=batch_created_at,
        )
        for forecast_date, quantity in monthly_predictions
    ]

    if not forecasts:
        raise ForecastCalculationError("Forecast calculation failure.")

    persisted = forecast_repository.create_forecasts(db, forecasts)
    return [_to_response(forecast) for forecast in persisted]


def list_forecasts(
    db: Session,
    *,
    product_id: str | None = None,
    method: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[ForecastResponse]:
    forecasts = forecast_repository.get_forecasts(
        db,
        product_id=product_id,
        method=method,
        start_date=start_date,
        end_date=end_date,
    )
    return [_to_response(forecast) for forecast in forecasts]


def get_forecasts_by_product(
    db: Session,
    product_id: str,
    *,
    method: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[ForecastResponse]:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ForecastProductNotFoundError("Product not found.")

    forecasts = forecast_repository.get_forecasts_by_product(
        db,
        product_id,
        method=method,
        start_date=start_date,
        end_date=end_date,
    )
    return [_to_response(forecast) for forecast in forecasts]


def get_forecast_summary(db: Session, product_id: str) -> ForecastSummaryResponse:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ForecastProductNotFoundError("Product not found.")

    sales_records = forecast_repository.get_sales_history(db, product_id)
    daily_history = _prepare_daily_history(sales_records)
    history_values = [quantity for _, quantity in daily_history]
    average_daily_demand = sum(history_values) / len(history_values)

    latest_batch = forecast_repository.get_forecast_summary(db, product_id=product_id)
    if latest_batch is None:
        raise ForecastHistoryNotFoundError("No forecast exists for this product.")

    first_forecast_date = forecast_repository.get_latest_forecast_batch(db, product_id=product_id, method=str(latest_batch["method"]))[0].forecast_date
    forecast_days = _count_days_in_months(first_forecast_date, int(latest_batch["forecast_horizon"]))
    forecast_demand = float(latest_batch["forecast_quantity_total"]) / forecast_days if forecast_days else 0.0
    growth_percentage = ((forecast_demand - average_daily_demand) / average_daily_demand * 100) if average_daily_demand else 0.0
    accuracy = calculate_forecast_accuracy(str(latest_batch["method"]), history_values)

    return ForecastSummaryResponse(
        product_id=product_id,
        average_daily_demand=float(average_daily_demand),
        forecast_demand=float(forecast_demand),
        growth_percentage=float(growth_percentage),
        method=str(latest_batch["method"]),
        forecast_horizon=int(latest_batch["forecast_horizon"]),
        confidence=float(latest_batch["confidence"]) if latest_batch["confidence"] is not None else None,
        accuracy=accuracy,
        accuracy_reason=None if accuracy is not None else "Not enough historical sales data for backtesting.",
    )
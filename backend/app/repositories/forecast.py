from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.forecast import Forecast
from app.models.sales_record import SalesRecord


def create_forecasts(db: Session, forecasts: list[Forecast]) -> list[Forecast]:
    db.add_all(forecasts)
    db.commit()
    for forecast in forecasts:
        db.refresh(forecast)
    return forecasts


def get_forecasts(
    db: Session,
    *,
    product_id: str | None = None,
    method: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Forecast]:
    query = select(Forecast)
    if product_id:
        query = query.where(Forecast.product_id == product_id)
    if method:
        query = query.where(Forecast.method == method)
    if start_date:
        query = query.where(Forecast.forecast_date >= start_date)
    if end_date:
        query = query.where(Forecast.forecast_date <= end_date)
    return db.scalars(query.order_by(Forecast.created_at.desc(), Forecast.forecast_date.asc())).all()


def get_forecasts_by_product(
    db: Session,
    product_id: str,
    *,
    method: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Forecast]:
    return get_forecasts(
        db,
        product_id=product_id,
        method=method,
        start_date=start_date,
        end_date=end_date,
    )


def get_latest_forecast_batch(
    db: Session,
    *,
    product_id: str,
    method: str | None = None,
) -> list[Forecast]:
    batch_query = select(func.max(Forecast.created_at)).where(Forecast.product_id == product_id)
    if method:
        batch_query = batch_query.where(Forecast.method == method)
    latest_created_at = db.scalar(batch_query)
    if latest_created_at is None:
        return []

    query = select(Forecast).where(Forecast.product_id == product_id, Forecast.created_at == latest_created_at)
    if method:
        query = query.where(Forecast.method == method)
    return db.scalars(query.order_by(Forecast.forecast_date.asc())).all()


def get_forecast_summary(
    db: Session,
    *,
    product_id: str,
    method: str | None = None,
) -> dict[str, object] | None:
    forecasts = get_latest_forecast_batch(db, product_id=product_id, method=method)
    if not forecasts:
        return None

    confidences = [float(forecast.confidence) for forecast in forecasts if forecast.confidence is not None]
    return {
        "product_id": product_id,
        "method": forecasts[0].method,
        "forecast_horizon": len(forecasts),
        "confidence": (sum(confidences) / len(confidences)) if confidences else None,
        "created_at": forecasts[0].created_at,
        "forecast_quantity_total": float(sum(float(forecast.forecast_quantity) for forecast in forecasts)),
    }


def get_sales_history(db: Session, product_id: str) -> list[SalesRecord]:
    query = select(SalesRecord).where(SalesRecord.product_id == product_id).order_by(SalesRecord.date.asc())
    return db.scalars(query).all()
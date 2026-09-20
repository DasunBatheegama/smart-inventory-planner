from __future__ import annotations

from datetime import date, timedelta
from io import BytesIO

import pytest

from app.agents.tools.forecast_tools import (
    ForecastToolProductNotFoundError,
    compare_forecast_periods,
    get_forecast_accuracy,
    get_forecast_summary,
    get_forecasts,
    get_product_forecast,
)
from app.db.database import SessionLocal


def product_payload(**overrides):
    payload = {
        "sku": "SKU-3001",
        "name": "Forecast Agent Widget",
        "category": "Electronics",
        "current_stock": 100,
        "unit_cost": 25,
        "lead_time": 7,
        "supplier": "Forecast Supplies",
        "reorder_point": 20,
        "safety_stock": 10,
    }
    payload.update(overrides)
    return payload


def upload_sales_csv(client, sku: str, start_date: date, days: int, quantity: int) -> None:
    rows = ["Date,SKU,Quantity Sold"]
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        rows.append(f"{current_date.isoformat()},{sku},{quantity}")
    response = client.post(
        "/api/v1/sales/upload",
        files={"file": ("sales.csv", BytesIO("\n".join(rows).encode("utf-8")), "text/csv")},
    )
    assert response.status_code == 200


def create_product(client, **overrides):
    response = client.post("/api/v1/products", json=product_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def seed_forecast(client, db, sku: str, days: int = 60, quantity: int = 10, horizon: int = 3):
    product = create_product(client, sku=sku)
    upload_sales_csv(client, product["sku"], date(2026, 1, 1), days, quantity)
    response = client.post(
        "/api/v1/forecasts/generate",
        json={"product_id": product["id"], "method": "moving_average", "forecast_horizon": horizon},
    )
    assert response.status_code == 201
    return product


def open_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def db():
    yield from open_session()


def test_get_product_forecast_returns_rows(client, db):
    product = seed_forecast(client, db, sku="SKU-3001")
    rows = get_product_forecast(db, product["id"])
    assert len(rows) == 3
    first = rows[0]
    assert first["product_id"] == product["id"]
    assert first["forecast_quantity"] == 300
    assert first["method"] == "moving_average"
    assert set(first.keys()) >= {"id", "product_id", "forecast_date", "forecast_quantity", "method", "confidence", "created_at"}


def test_get_product_forecast_missing_forecast_returns_empty(client, db):
    product = create_product(client, sku="SKU-3002")
    assert get_product_forecast(db, product["id"]) == []


def test_get_product_forecast_invalid_product_raises(client, db):
    with pytest.raises(ForecastToolProductNotFoundError):
        get_product_forecast(db, "missing-product")


def test_get_forecast_summary_returns_data(client, db):
    product = seed_forecast(client, db, sku="SKU-3003")
    summary = get_forecast_summary(db, product["id"])
    assert summary is not None
    assert summary["product_id"] == product["id"]
    assert summary["method"] == "moving_average"
    assert summary["forecast_horizon"] == 3
    assert summary["forecast_demand"] == 10


def test_get_forecast_summary_unavailable_when_no_forecast(client, db):
    product = create_product(client, sku="SKU-3004")
    assert get_forecast_summary(db, product["id"]) is None


def test_get_forecast_summary_invalid_product_raises(client, db):
    with pytest.raises(ForecastToolProductNotFoundError):
        get_forecast_summary(db, "missing-product")


def test_get_forecast_accuracy_with_enough_history(client, db):
    product = seed_forecast(client, db, sku="SKU-3005", days=60)
    accuracy = get_forecast_accuracy(db, product["id"])
    assert accuracy is not None
    assert accuracy["mae"] == 0
    assert accuracy["mape"] == 0


def test_get_forecast_accuracy_missing_with_short_history(client, db):
    product = seed_forecast(client, db, sku="SKU-3006", days=40)
    assert get_forecast_accuracy(db, product["id"]) is None


def test_get_forecast_accuracy_unavailable_when_no_forecast(client, db):
    product = create_product(client, sku="SKU-3007")
    assert get_forecast_accuracy(db, product["id"]) is None


def test_get_forecasts_with_filters(client, db):
    product = seed_forecast(client, db, sku="SKU-3008")
    rows = get_forecasts(db, {"product_id": product["id"], "method": "moving_average"})
    assert len(rows) == 3
    assert all(row["product_id"] == product["id"] for row in rows)

    all_rows = get_forecasts(db, {})
    assert len(all_rows) == 3


def test_get_forecasts_invalid_product_raises(client, db):
    with pytest.raises(ForecastToolProductNotFoundError):
        get_forecasts(db, {"product_id": "missing-product"})


def test_compare_forecast_periods_returns_comparison(client, db):
    product = seed_forecast(client, db, sku="SKU-3009", horizon=3)
    comparison = compare_forecast_periods(db, product["id"])
    assert comparison is not None
    assert comparison["latest_period"] == "2026-06-01"
    assert comparison["previous_period"] == "2026-05-01"
    assert comparison["latest_quantity"] == 300
    assert comparison["previous_quantity"] == 310
    assert comparison["absolute_change"] == -10
    assert comparison["percent_change"] == pytest.approx(-3.23, abs=0.01)


def test_compare_forecast_periods_none_for_single_period(client, db):
    product = seed_forecast(client, db, sku="SKU-3010", horizon=1)
    assert compare_forecast_periods(db, product["id"]) is None


def test_compare_forecast_periods_invalid_product_raises(client, db):
    with pytest.raises(ForecastToolProductNotFoundError):
        compare_forecast_periods(db, "missing-product")
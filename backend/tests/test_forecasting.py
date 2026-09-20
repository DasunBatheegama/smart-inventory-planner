from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from io import BytesIO


def product_payload(**overrides):
    payload = {
        "sku": "SKU-2001",
        "name": "Forecast Widget",
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


def expected_monthly_total(month_start: date, daily_quantity: int) -> int:
    return monthrange(month_start.year, month_start.month)[1] * daily_quantity


def generate_forecast(client, payload: dict):
    response = client.post("/api/v1/forecasts/generate", json=payload)
    return response


def seed_constant_history(client, *, sku: str, days: int = 60, quantity: int = 10) -> None:
    upload_sales_csv(client, sku, date(2026, 1, 1), days, quantity)


def test_moving_average_forecast_generation(client):
    product = create_product(client)
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["forecast_date"] == "2026-04-01"
    assert data[0]["forecast_quantity"] == expected_monthly_total(date(2026, 4, 1), 10)
    assert data[0]["method"] == "moving_average"


def test_exponential_smoothing_forecast_generation(client):
    product = create_product(client, sku="SKU-2002")
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "exponential_smoothing", "forecast_horizon": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["forecast_date"] == "2026-04-01"
    assert data[0]["forecast_quantity"] == expected_monthly_total(date(2026, 4, 1), 10)
    assert data[0]["method"] == "exponential_smoothing"


def test_three_month_forecast_and_list_endpoints(client):
    product = create_product(client, sku="SKU-2003")
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 3},
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 3
    assert [item["forecast_date"] for item in data] == ["2026-04-01", "2026-05-01", "2026-06-01"]
    assert [item["forecast_quantity"] for item in data] == [300, 310, 300]

    all_forecasts = client.get("/api/v1/forecasts")
    assert all_forecasts.status_code == 200
    assert len(all_forecasts.json()) == 3

    product_forecasts = client.get(f"/api/v1/forecasts/{product['id']}")
    assert product_forecasts.status_code == 200
    assert len(product_forecasts.json()) == 3

    filtered = client.get(f"/api/v1/forecasts?product_id={product['id']}&method=moving_average")
    assert filtered.status_code == 200
    assert len(filtered.json()) == 3


def test_invalid_product(client):
    response = generate_forecast(
        client,
        {"product_id": "missing-product", "method": "moving_average", "forecast_horizon": 1},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found."


def test_missing_sales_data(client):
    product = create_product(client, sku="SKU-2004")

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 1},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "No sales history exists for this product."


def test_insufficient_sales_history(client):
    product = create_product(client, sku="SKU-2005")
    upload_sales_csv(client, product["sku"], date(2026, 1, 1), 10, 10)

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 1},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient historical sales data. At least 30 days are required."


def test_invalid_forecasting_method(client):
    product = create_product(client, sku="SKU-2006")
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "unsupported", "forecast_horizon": 1},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid forecasting method."


def test_invalid_forecast_horizon(client):
    product = create_product(client, sku="SKU-2007")
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 2},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid forecast horizon."


def test_forecast_summary_and_accuracy(client):
    product = create_product(client, sku="SKU-2008")
    seed_constant_history(client, sku=product["sku"])

    response = generate_forecast(
        client,
        {"product_id": product["id"], "method": "moving_average", "forecast_horizon": 3},
    )
    assert response.status_code == 201

    summary_response = client.get(f"/api/v1/forecasts/{product['id']}/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["product_id"] == product["id"]
    assert summary["average_daily_demand"] == 10
    assert summary["forecast_demand"] == 10
    assert summary["growth_percentage"] == 0
    assert summary["method"] == "moving_average"
    assert summary["forecast_horizon"] == 3
    assert summary["confidence"] == 100
    assert summary["accuracy"] is not None
    assert summary["accuracy"]["mae"] == 0
    assert summary["accuracy"]["mape"] == 0
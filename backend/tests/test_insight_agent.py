from __future__ import annotations

import io
import csv
import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _seed_sales_csv(client: TestClient, sku: str) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Date", "SKU", "Quantity Sold"])
    for day in range(1, 61):
        writer.writerow([f"2024-01-{day:02d}", sku, 8 + (day % 5)])
    response = client.post(
        "/api/v1/sales/upload",
        files={"file": ("sales.csv", buffer.getvalue().encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200, response.text


def _create_product(client: TestClient, sku: str) -> int:
    response = client.post(
        "/api/v1/products",
        json={"name": "Insight Widget", "sku": sku, "unit": "pcs"},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _stock_on_hand(client: TestClient, product_id: int, quantity: int) -> None:
    response = client.post(
        "/api/v1/inventory/adjustments",
        json={"product_id": product_id, "quantity": quantity, "reason": "stocktake"},
    )
    assert response.status_code == 200, response.text


def _generate_forecast(client: TestClient, product_id: int) -> None:
    forecast = client.post(
        "/api/v1/forecasts/generate",
        json={"product_id": product_id, "method": "moving_average", "forecast_horizon": 3},
    )
    assert forecast.status_code == 201, forecast.text
    plan = client.post(
        "/api/v1/planning/generate",
        json={"product_id": product_id, "service_level": 0.95, "lead_time": 7},
    )
    assert plan.status_code == 200, plan.text


def _generate_alerts(client: TestClient) -> None:
    response = client.post("/api/v1/alerts/generate")
    assert response.status_code == 200, response.text


def _post(client: TestClient, question: str, product_id: int | None = None) -> dict:
    payload: dict = {"question": question}
    if product_id is not None:
        payload["product_id"] = str(product_id)
    response = client.post("/api/v1/agents/insights", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_insight_agent_full_report(client: TestClient) -> None:
    sku = _unique("INSIGHT")
    product_id = _create_product(client, sku)
    _seed_sales_csv(client, sku)
    _generate_forecast(client, product_id)
    _stock_on_hand(client, product_id, 200)
    _generate_alerts(client)

    body = _post(client, "What should I focus on this week?")
    assert body["question"] == "What should I focus on this week?"


def test_insight_agent_product_scoped(client: TestClient) -> None:
    sku = _unique("INSIGHT")
    product_id = _create_product(client, sku)
    _seed_sales_csv(client, sku)
    _generate_forecast(client, product_id)
    _stock_on_hand(client, product_id, 60)
    _generate_alerts(client)

    body = _post(client, "Anything urgent on this product?", product_id=product_id)
    assert body["question"] == "Anything urgent on this product?"


def test_insight_agent_unknown_product(client: TestClient) -> None:
    response = client.post(
        "/api/v1/agents/insights",
        json={
            "question": "report please",
            "product_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert response.status_code == 404, response.text


def test_insight_agent_list_required(client: TestClient) -> None:
    response = client.post("/api/v1/agents/insights", json={"question": ""})
    assert response.status_code == 422, response.text

from __future__ import annotations

import json
from datetime import date, timedelta
from io import BytesIO

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.forecast_agent import (
    ForecastAgent,
    ForecastAgentLLMError,
    ForecastAgentProductNotFoundError,
    ForecastAgentResponseError,
)
from app.api.routes.agents import get_forecast_agent
from app.db.database import get_db
from app.schemas.agent import ForecastAgentResponse
from app.services.ai.llm_service import LLMConfigurationError, LLMService, LLMTimeoutError


def make_narrative(summary="The forecast is 300 units for the coming month.", insights=None, recommendations=None):
    return json.dumps(
        {
            "summary": summary,
            "insights": insights or ["Demand is stable."],
            "recommendations": recommendations or ["Keep current stock levels."],
        }
    )


class FakeLLMService(LLMService):
    def __init__(self, response_text: str, error: Exception | None = None) -> None:
        LLMService.__init__(self, api_key="test-key", model="gpt-test")
        self._response_text = response_text
        self._error = error
        self.last_system_prompt: str | None = None
        self.last_user_message: str | None = None

    def complete(self, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        if self._error is not None:
            raise self._error
        return self._response_text


def product_payload(**overrides):
    payload = {
        "sku": "SKU-4001",
        "name": "Agent Widget",
        "category": "Electronics",
        "current_stock": 100,
        "unit_cost": 25,
        "lead_time": 7,
        "supplier": "Agent Supplies",
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


def seed_forecast(client, sku: str, days: int = 60, quantity: int = 10, horizon: int = 3):
    product = create_product(client, sku=sku)
    upload_sales_csv(client, product["sku"], date(2026, 1, 1), days, quantity)
    response = client.post(
        "/api/v1/forecasts/generate",
        json={"product_id": product["id"], "method": "moving_average", "forecast_horizon": horizon},
    )
    assert response.status_code == 201
    return product


def build_agent(db, fake_llm):
    return ForecastAgent(llm_service=fake_llm, db=db)


class TestForecastAgent:
    def test_valid_forecast_returns_structured_response(self, client, db):
        product = seed_forecast(client, sku="SKU-4001")
        fake = FakeLLMService(make_narrative())
        agent = build_agent(db, fake)

        response = agent.invoke("What is the forecast for this product?", product_id=product["id"])

        assert isinstance(response, ForecastAgentResponse)
        assert response.agent == "forecast_agent"
        assert response.summary == "The forecast is 300 units for the coming month."
        assert response.insights == ["Demand is stable."]
        assert response.recommendations == ["Keep current stock levels."]
        assert len(response.data["product_forecast"]) == 3
        assert response.data["forecast_accuracy"] is not None
        assert response.data["period_comparison"] is not None
        assert fake.last_system_prompt is not None
        assert "DATA" in fake.last_user_message

    def test_missing_forecast_data_unavailable(self, client, db):
        product = create_product(client, sku="SKU-4002")
        fake = FakeLLMService(make_narrative(summary="No forecast data is available for this product."))
        agent = build_agent(db, fake)

        response = agent.invoke("What is the forecast?", product_id=product["id"])

        assert response.data["product_forecast"] == []
        assert response.data["forecast_summary"] is None
        assert response.data["forecast_accuracy"] is None
        assert response.data["period_comparison"] is None
        assert "No forecast data is available" in response.summary

    def test_invalid_product_raises(self, client, db):
        fake = FakeLLMService(make_narrative())
        agent = build_agent(db, fake)
        with pytest.raises(ForecastAgentProductNotFoundError) as exc_info:
            agent.invoke("Explain the forecast", product_id="missing-product")
        assert "not found" in str(exc_info.value).lower()

    def test_missing_accuracy(self, client, db):
        product = seed_forecast(client, sku="SKU-4003", days=40)
        fake = FakeLLMService(make_narrative())
        agent = build_agent(db, fake)

        response = agent.invoke("What is the forecast accuracy?", product_id=product["id"])

        assert response.data["forecast_accuracy"] is None
        assert len(response.data["product_forecast"]) == 3

    def test_question_without_product_id_includes_all_forecasts(self, client, db):
        product = seed_forecast(client, sku="SKU-4004")
        fake = FakeLLMService(make_narrative())
        agent = build_agent(db, fake)

        response = agent.invoke("Which products have high forecast demand?")

        assert len(response.data["forecasts"]) == 3
        assert all("product" in row for row in response.data["forecasts"])
        assert response.data["forecasts"][0]["product"]["sku"] == product["sku"]

    def test_llm_error_is_safe(self, client, db):
        product = seed_forecast(client, sku="SKU-4005")
        fake = FakeLLMService(make_narrative(), error=LLMTimeoutError("LLM request timed out."))
        agent = build_agent(db, fake)

        with pytest.raises(ForecastAgentLLMError) as exc_info:
            agent.invoke("Explain the forecast", product_id=product["id"])
        assert "timed out" in str(exc_info.value).lower()

    def test_missing_api_key_is_safe(self, client, db):
        product = seed_forecast(client, sku="SKU-4006")
        fake = FakeLLMService(make_narrative(), error=LLMConfigurationError("LLM is not configured. Set the provider API key."))
        agent = build_agent(db, fake)

        with pytest.raises(ForecastAgentLLMError) as exc_info:
            agent.invoke("Explain the forecast", product_id=product["id"])
        assert "provider API key" in str(exc_info.value)

    def test_malformed_llm_output_raises(self, client, db):
        product = seed_forecast(client, sku="SKU-4007")
        fake = FakeLLMService("this is not json")
        agent = build_agent(db, fake)

        with pytest.raises(ForecastAgentResponseError):
            agent.invoke("Explain the forecast", product_id=product["id"])

    def test_llm_output_with_json_fence_is_parsed(self, client, db):
        product = seed_forecast(client, sku="SKU-4008")
        fence = "```json\n" + make_narrative() + "\n```"
        fake = FakeLLMService(fence)
        agent = build_agent(db, fake)

        response = agent.invoke("Explain the forecast", product_id=product["id"])
        assert response.summary == "The forecast is 300 units for the coming month."

    def test_llm_empty_summary_is_rejected(self, client, db):
        product = seed_forecast(client, sku="SKU-4009")
        fake = FakeLLMService(json.dumps({"summary": "   ", "insights": [], "recommendations": []}))
        agent = build_agent(db, fake)

        with pytest.raises(ForecastAgentResponseError):
            agent.invoke("Explain the forecast", product_id=product["id"])


@pytest.fixture()
def db():
    from app.db.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_agent_with(fake_llm):
    def dependency(db: Session = Depends(get_db)) -> ForecastAgent:
        return ForecastAgent(llm_service=fake_llm, db=db)

    return dependency


class TestForecastAgentEndpoint:
    def test_endpoint_valid_question(self, client):
        product = seed_forecast(client, sku="SKU-4101")
        fake = FakeLLMService(make_narrative())
        client.app.dependency_overrides[get_forecast_agent] = override_agent_with(fake)
        try:
            response = client.post(
                "/api/v1/agents/forecast",
                json={"question": "What is the forecast for this product?", "product_id": product["id"]},
            )
        finally:
            client.app.dependency_overrides.pop(get_forecast_agent, None)

        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "forecast_agent"
        assert data["summary"] == "The forecast is 300 units for the coming month."
        assert data["insights"] == ["Demand is stable."]
        assert data["recommendations"] == ["Keep current stock levels."]
        assert len(data["data"]["product_forecast"]) == 3

    def test_endpoint_missing_forecast_returns_ok(self, client):
        product = create_product(client, sku="SKU-4102")
        fake = FakeLLMService(make_narrative(summary="No forecast data is available for this product."))
        client.app.dependency_overrides[get_forecast_agent] = override_agent_with(fake)
        try:
            response = client.post(
                "/api/v1/agents/forecast",
                json={"question": "What is the forecast?", "product_id": product["id"]},
            )
        finally:
            client.app.dependency_overrides.pop(get_forecast_agent, None)

        assert response.status_code == 200
        assert response.json()["data"]["product_forecast"] == []

    def test_endpoint_invalid_product_returns_404(self, client):
        fake = FakeLLMService(make_narrative())
        client.app.dependency_overrides[get_forecast_agent] = override_agent_with(fake)
        try:
            response = client.post(
                "/api/v1/agents/forecast",
                json={"question": "What is the forecast?", "product_id": "missing-product"},
            )
        finally:
            client.app.dependency_overrides.pop(get_forecast_agent, None)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_endpoint_validation_rejects_short_question(self, client):
        response = client.post("/api/v1/agents/forecast", json={"question": "hi"})
        assert response.status_code == 422

    def test_endpoint_validation_rejects_blank_question(self, client):
        response = client.post("/api/v1/agents/forecast", json={"question": "   "})
        assert response.status_code == 422

    def test_endpoint_validation_accepts_blank_product_id(self, client):
        product = seed_forecast(client, sku="SKU-4103")
        fake = FakeLLMService(make_narrative())
        client.app.dependency_overrides[get_forecast_agent] = override_agent_with(fake)
        try:
            response = client.post(
                "/api/v1/agents/forecast",
                json={"question": "What is the forecast?", "product_id": "  "},
            )
        finally:
            client.app.dependency_overrides.pop(get_forecast_agent, None)

        assert response.status_code == 200
        assert response.json()["data"].get("product_id") is None

    def test_endpoint_llm_error_returns_502(self, client):
        product = seed_forecast(client, sku="SKU-4104")
        fake = FakeLLMService(make_narrative(), error=LLMTimeoutError("LLM request timed out."))
        client.app.dependency_overrides[get_forecast_agent] = override_agent_with(fake)
        try:
            response = client.post(
                "/api/v1/agents/forecast",
                json={"question": "What is the forecast?", "product_id": product["id"]},
            )
        finally:
            client.app.dependency_overrides.pop(get_forecast_agent, None)

        assert response.status_code == 502
        assert "timed out" in response.json()["detail"].lower()
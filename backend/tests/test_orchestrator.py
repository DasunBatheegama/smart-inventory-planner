"""Stage-5B orchestration tests.

Mirrors the committed agent test suite: every LLM interaction is mocked, the
orchestrator is built over the committed forecast/inventory factories (the two
registered BaseAgent implementations) plus a test-local BaseAgent-conforming
insight stub, and every scenario runs against the real endpoint + dependencies
so routing, the allowlist registry, and the error mapping (404 unknown / 502
LLM / 500 execution) are exercised end to end.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from io import BytesIO

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import (
    AIOrchestrator,
    OrchestratorAgentExecutionError,
    OrchestratorError,
    OrchestratorLLMError,
    OrchestratorResponseError,
    OrchestratorUnknownAgentError,
    route_question,
)
from app.agents.base import BaseAgent
from app.api.routes.agents import get_orchestrator
from app.services.ai.agent_service import AgentRegistry
from app.services.ai.llm_service import (
    LLMService,
    LLMConfigurationError,
    LLMTimeoutError,
)
from app.schemas.agent import (
    ForecastAgentResponse,
    InsightAgentResponse,
    InventoryAgentResponse,
    OrchestratorResponse,
)
from app.db.database import get_db


class FakeLLMService(LLMService):
    """Deterministic LLM stub that routes responses per agent name.

    The orchestrator drives exactly one LLM completion per matched agent, so a
    single stub with a per-agent response table keeps all scenarios free of
    real network calls while still exercising multi-agent combination.
    """

    def __init__(self, responses: dict[str, str], error: Exception | None = None) -> None:
        LLMService.__init__(self, api_key="test-key", model="gpt-test")
        self._responses = responses
        self._error = error
        self.last_system_prompt: str | None = None
        self.last_user_message: str | None = None

    def complete(self, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        if self._error is not None:
            raise self._error
        if "" in self._responses:
            return self._responses[""]
        lowered = user_message.lower()
        if "insight" in lowered or "suggest" in lowered or "slow" in lowered:
            return self._responses.get("insight", "")
        if "forecast" in lowered:
            return self._responses.get("forecast", "")
        return self._responses.get("inventory", "")

    def fail_next(self, error: Exception) -> None:
        self._error = error

    def clear_error(self) -> None:
        self._error = None


def forecast_narrative() -> str:
    return json.dumps(
        {
            "summary": "The forecast for the coming month is 300 units.",
            "insights": ["Demand is stable."],
            "recommendations": ["Keep current stock levels."],
            "data": {"product_forecast": [{"period": "2026-02-01", "quantity": 100}]},
        }
    )


def inventory_narrative() -> str:
    return json.dumps(
        {
            "summary": "Inventory is healthy; reorder 20 units in the next cycle.",
            "insights": ["2 weeks of stock remaining."],
            "recommendations": ["Reorder 20 units."],
            "data": {"current_stock": 45, "recommended_order": 20},
        }
    )


def insight_narrative() -> str:
    return json.dumps(
        {
            "summary": "Insight suggests pruning slow-moving SKUs to free cash.",
            "insights": ["SKU has 6 weeks of cover."],
            "recommendations": ["Review and prune low-margin slow movers."],
            "data": {"alerts": [], "recommendations": ["Review slow movers."]},
        }
    )


def default_responses() -> dict[str, str]:
    return {
        "forecast": forecast_narrative(),
        "inventory": inventory_narrative(),
        "insight": insight_narrative(),
    }


class FakeForecastAgent(BaseAgent):
    name = "forecast_agent"
    system_prompt = "You are a test forecast assistant."

    def __init__(self, llm_service: FakeLLMService, db: Session) -> None:
        BaseAgent.__init__(self, name=self.name, system_prompt=self.system_prompt, llm_service=llm_service)
        self.db = db

    def invoke(self, question: str, product_id: str | None = None) -> ForecastAgentResponse:
        narrative = json.loads(self.llm_service.complete(self.system_prompt, question))
        return ForecastAgentResponse(
            agent="forecast_agent",
            summary=narrative["summary"],
            insights=narrative.get("insights", []),
            recommendations=narrative.get("recommendations", []),
            data=narrative.get("data", {}),
        )


class FakeInventoryAgent(BaseAgent):
    name = "inventory_agent"
    system_prompt = "You are a test inventory assistant."

    def __init__(self, llm_service: FakeLLMService, db: Session) -> None:
        BaseAgent.__init__(self, name=self.name, system_prompt=self.system_prompt, llm_service=llm_service)
        self.db = db

    def invoke(self, question: str, product_id: str | None = None) -> InventoryAgentResponse:
        narrative = json.loads(self.llm_service.complete(self.system_prompt, question))
        return InventoryAgentResponse(
            agent="inventory_agent",
            summary=narrative["summary"],
            insights=narrative.get("insights", []),
            recommendations=narrative.get("recommendations", []),
            data=narrative.get("data", {}),
        )


class FakeInsightAgent(BaseAgent):
    name = "insight_agent"
    system_prompt = "You are a test insight assistant."

    def __init__(self, llm_service: FakeLLMService, db: Session) -> None:
        BaseAgent.__init__(self, name=self.name, system_prompt=self.system_prompt, llm_service=llm_service)
        self.db = db

    def invoke(self, question: str, product_id: str | None = None) -> InsightAgentResponse:
        narrative = json.loads(self.llm_service.complete(self.system_prompt, question))
        return InsightAgentResponse(
            agent="insight_agent",
            question=question,
            summary=narrative["summary"],
            insights=narrative.get("insights", []),
            recommendations=narrative.get("recommendations", []),
        )


# ---------------------------------------------------------------------------
# Seed helpers (deterministic contract mirroring committed agent tests)
# ---------------------------------------------------------------------------
def product_payload(**overrides) -> dict:
    payload = {
        "sku": "SKU-6001",
        "name": "Orchestrator Widget",
        "category": "Electronics",
        "current_stock": 100,
        "unit_cost": 25,
        "lead_time": 7,
        "supplier": "Orchestration Supplies",
        "reorder_point": 20,
        "safety_stock": 10,
    }
    payload.update(overrides)
    return payload


def create_product(client, **overrides) -> dict:
    response = client.post("/api/v1/products", json=product_payload(**overrides))
    assert response.status_code == 201
    return response.json()


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


def seed_forecast(client, sku: str = "SKU-6001", days: int = 60, quantity: int = 10) -> dict:
    product = create_product(client, sku=sku)
    upload_sales_csv(client, product["sku"], date(2026, 1, 1), days, quantity)
    response = client.post(
        "/api/v1/forecasts/generate",
        json={"product_id": product["id"], "method": "moving_average", "forecast_horizon": 3},
    )
    assert response.status_code == 201
    return product


def seed_inventory(client, sku: str = "SKU-6001", quantity: int = 100, lead_time: int = 7) -> dict:
    product = seed_forecast(client, sku=sku)
    response = client.post(
        "/api/v1/planning/generate",
        json={"product_id": product["id"], "lead_time": lead_time},
    )
    assert response.status_code == 200
    return product


def seed_full(client, sku: str = "SKU-6001") -> dict:
    return seed_inventory(client, sku=sku)


# ---------------------------------------------------------------------------
# Orchestrator builder mirrored on the committed allowlist registry contract
# ---------------------------------------------------------------------------
def build_orchestrator(db: Session, fake: FakeLLMService) -> AIOrchestrator:
    from app.agents.forecast_agent import create_forecast_agent
    from app.agents.inventory_agent import create_inventory_agent

    forecast_agent = create_forecast_agent(db, llm_service=fake)
    inventory_agent =     create_inventory_agent(db, llm_service=fake)
    insight_agent = FakeInsightAgent(fake, db)

    registry = AgentRegistry()
    registry.register(forecast_agent)
    registry.register(inventory_agent)
    registry.register(insight_agent)

    return AIOrchestrator(registry=registry)


def override_orchestrator_with(db: Session, fake: FakeLLMService):
    def dependency(db_session: Session = Depends(get_db)) -> AIOrchestrator:
        return build_orchestrator(db_session, fake)

    return dependency


# ---------------------------------------------------------------------------
# Stage-5B scenarios: every request goes through the REAL committed endpoint
# (/api/v1/agents/orchestrator) with the orchestrator dependency overridden to
# the deterministic builder above, so routing, the registry allowlist, and the
# 404/502/500 error mapping are all exercised end to end.
# ---------------------------------------------------------------------------


@pytest.fixture()
def db():
    from app.db.database import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def overridden_orchestrator(client, db):
    fake = FakeLLMService(default_responses())
    dependency = override_orchestrator_with(db, fake)
    from app.api.routes.agents import get_orchestrator

    client.app.dependency_overrides[get_orchestrator] = dependency
    try:
        yield client, db, fake
    finally:
        client.app.dependency_overrides.pop(get_orchestrator, None)


def post_orchestrator(client, message: str, *, product_id: str | None = None):
    payload = {"message": message}
    if product_id is not None:
        payload["product_id"] = product_id
    return client.post("/api/v1/agents/orchestrator", json=payload)


# --- 10 committed-contract scenarios --------------------------------------

def test_orchestrator_routes_forecast_question(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(client, "What is the forecast for the coming month?")
    assert response.status_code == 200
    body = response.json()
    assert body["agent"] == "orchestrator"
    assert "forecast_agent" in body["agents_used"]
    assert body["summary"]


def test_orchestrator_routes_inventory_question(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(client, "How much should we reorder and why?")
    assert response.status_code == 200
    body = response.json()
    assert "inventory_agent" in body["agents_used"]
    assert "inventory_agent" in body["supporting_data"]


def test_orchestrator_routes_insight_question(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(client, "What insights should we prioritize for slow movers?")
    assert response.status_code == 200
    body = response.json()
    assert "insight_agent" in body["agents_used"]


def test_orchestrator_combines_product_scoped_forecast(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    product = seed_forecast(client, sku="SKU-6010")
    response = post_orchestrator(
        client,
        "What is the forecast for SKU-6010?",
        product_id=product["id"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "forecast_agent" in body["agents_used"]
    assert "forecast_agent" in body["supporting_data"]


def test_orchestrator_combines_product_scoped_inventory(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    product = seed_inventory(client, sku="SKU-6011")
    response = post_orchestrator(
        client,
        "Is our inventory healthy for SKU-6011?",
        product_id=product["id"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "inventory_agent" in body["agents_used"]
    assert "inventory_agent" in body["supporting_data"]


def test_orchestrator_multi_agent_combine(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    product = seed_forecast(client, sku="SKU-6012")
    response = post_orchestrator(
        client,
        "What is the forecast and is the inventory health good?",
        product_id=product["id"],
    )
    assert response.status_code == 200
    body = response.json()
    assert "forecast_agent" in body["agents_used"]
    assert "inventory_agent" in body["agents_used"]


def test_orchestrator_unknown_question_is_404(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(client, "Tell me a joke about warehouse robots.")
    assert response.status_code == 404


def test_orchestrator_llm_failure_is_502(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    from app.services.ai.llm_service import LLMServiceError

    fake.fail_next(LLMServiceError("boom"))

    response = post_orchestrator(client, "What is the forecast for the coming month?")
    assert response.status_code == 502


def test_orchestrator_response_payload_shape(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(client, "What insights should we prioritize for slow movers?")
    assert response.status_code == 200
    body = response.json()
    for field in ("agent", "question", "summary", "agents_used", "supporting_data", "recommendations"):
        assert field in body


def test_orchestrator_missing_product_is_500(overridden_orchestrator) -> None:
    client, db, fake = overridden_orchestrator
    response = post_orchestrator(
        client,
        "What is the forecast for the coming month?",
        product_id="00000000-0000-0000-0000-000000000000",
    )
    assert response.status_code == 500

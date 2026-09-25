from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.api.routes.agents import get_orchestrator
from tests.test_orchestrator import (  # noqa: F401
    FakeLLMService,
    build_orchestrator,
    db,
    default_responses,
    post_orchestrator,
    seed_forecast,
    seed_inventory,
)


@pytest.fixture()
def chat_client(client, db):
    fake = FakeLLMService(default_responses())
    client.app.dependency_overrides[get_orchestrator] = lambda: build_orchestrator(db, fake)
    try:
        yield client, fake
    finally:
        client.app.dependency_overrides.pop(get_orchestrator, None)


def post_chat(client, message: str, *, product_id: str | None = None):
    payload: dict = {"message": message}
    if product_id is not None:
        payload["product_id"] = product_id
    return client.post("/api/v1/agents/chat", json=payload)


def test_chat_returns_answer_for_forecast_question(chat_client) -> None:
    client, _fake = chat_client
    response = post_chat(client, "What is the forecast for the coming month?")
    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert "forecast_agent" in body["agents_used"]


def test_chat_response_shape(chat_client) -> None:
    client, _fake = chat_client
    response = post_chat(client, "How much should we reorder?")
    assert response.status_code == 200
    body = response.json()
    for field in ("answer", "agents_used", "supporting_data", "recommendations"):
        assert field in body


def test_chat_rejects_blank_message(chat_client) -> None:
    client, _fake = chat_client
    response = client.post("/api/v1/agents/chat", json={"message": "  "})
    assert response.status_code == 422


def test_chat_rejects_missing_message(chat_client) -> None:
    client, _fake = chat_client
    response = client.post("/api/v1/agents/chat", json={})
    assert response.status_code == 422


def test_chat_rejects_too_long_message(chat_client) -> None:
    client, _fake = chat_client
    response = post_chat(client, "a" * 501)
    assert response.status_code == 422


def test_chat_unknown_question_is_404(chat_client) -> None:
    client, _fake = chat_client
    response = post_chat(client, "Tell me a joke about warehouse robots.")
    assert response.status_code == 404


def test_chat_llm_failure_is_502(chat_client) -> None:
    client, fake = chat_client
    from app.services.ai.llm_service import LLMServiceError

    fake.fail_next(LLMServiceError("boom"))
    response = post_chat(client, "What is the forecast for the coming month?")
    assert response.status_code == 502


def test_chat_missing_product_is_500(chat_client) -> None:
    client, _fake = chat_client
    response = post_chat(
        client,
        "What is the forecast for the coming month?",
        product_id="00000000-0000-0000-0000-000000000000",
    )
    assert response.status_code == 500


def test_chat_product_scoped_forecast(chat_client) -> None:
    client, _fake = chat_client
    product = seed_forecast(client, sku="SKU-7001")
    response = post_chat(
        client,
        "What is the forecast for SKU-7001?",
        product_id=product["id"],
    )
    assert response.status_code == 200
    assert "forecast_agent" in response.json()["agents_used"]


def test_chat_product_scoped_inventory(chat_client) -> None:
    client, _fake = chat_client
    product = seed_inventory(client, sku="SKU-7002")
    response = post_chat(
        client,
        "Is our inventory healthy for SKU-7002?",
        product_id=product["id"],
    )
    assert response.status_code == 200
    assert "inventory_agent" in response.json()["agents_used"]


def test_status_reports_all_agents_available(chat_client) -> None:
    client, _fake = chat_client
    response = client.get("/api/v1/agents/status")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "orchestrator": "available",
        "forecast_agent": "available",
        "inventory_agent": "available",
        "insight_agent": "available",
    }


def test_status_and_chat_share_the_orchestrator_dependency(client) -> None:
    from app.agents.orchestrator import AIOrchestrator
    from app.services.ai.agent_service import AgentRegistry

    registry = AgentRegistry()
    empty = AIOrchestrator(registry=registry)
    client.app.dependency_overrides[get_orchestrator] = lambda: empty
    try:
        response = client.get("/api/v1/agents/status")
        assert response.status_code == 200
        assert response.json()["forecast_agent"] == "unavailable"
        assert response.json()["insight_agent"] == "unavailable"
    finally:
        client.app.dependency_overrides.pop(get_orchestrator, None)


def test_orchestrator_endpoint_remains_available(chat_client) -> None:
    client, _fake = chat_client
    response = post_orchestrator(client, "What is the forecast for the coming month?")
    assert response.status_code == 200
    assert response.json()["agent"] == "orchestrator"

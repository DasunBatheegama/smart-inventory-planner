from __future__ import annotations

import json
from datetime import date, timedelta
from io import BytesIO

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.inventory_agent import (
    InventoryAgent,
    InventoryAgentLLMError,
    InventoryAgentProductNotFoundError,
    InventoryAgentResponseError,
)
from app.api.routes.agents import get_inventory_agent
from app.db.database import get_db
from app.schemas.agent import InventoryAgentResponse
from app.services.ai.llm_service import LLMConfigurationError, LLMService, LLMTimeoutError


# --- narrative helpers (mirror forecast agent tests) ---


def make_narrative(summary: str | None = None, insights=None, recommendations=None):
    return json.dumps(
        {
            "summary": summary or "The plan is 250 units for the coming month.",
            "insights": insights or ["Inventory health is stable."],
            "recommendations": recommendations or ["Continue with the current plan."],
        }
    )


def narrative(**overrides):
    return make_narrative()


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


def complete_error(message: str = "The inventory agent timed out.") -> str:
    return message


# --- seeding helpers (mirror test_forecast_agent.py) ---


def product_payload(**overrides):
    payload = {
        "sku": "SKU-6001",
        "name": "Inventory Agent Widget",
        "category": "Electronics",
        "current_stock": 120,
        "unit_cost": 25,
        "lead_time": 7,
        "supplier": "Inventory Supplies",
        "reorder_point": 20,
        "safety_stock": 10,
    }
    payload.update(overrides)
    return payload


def create_product(client, **overrides):
    response = client.post("/api/v1/products", json=product_payload(**overrides))
    assert response.status_code == 201
    return response.json()


def seed_inventory(client, sku: str, days: int = 60, quantity: int = 10, service_level: float = 0.95):
    product = create_product(client, sku=sku)
    upload_planning_csv(client, product["sku"], date(2026, 1, 1), days, quantity)
    response = client.post(
        "/api/v1/planning/generate",
        json={
            "product_id": product["id"],
            "service_level": service_level,
        },
    )
    assert response.status_code == 200
    return product

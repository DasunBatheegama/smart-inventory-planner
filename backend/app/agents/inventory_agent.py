from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.prompts.inventory_prompt import INVENTORY_AGENT_SYSTEM_PROMPT
from app.agents.tools.inventory_tools import (
    InventoryToolError,
    InventoryToolProductNotFoundError,
    generate_plan_for_product as tool_generate_plan_for_product,
    generate_plans_for_all_products as tool_generate_plans_for_all_products,
    get_inventory_health as tool_get_inventory_health,
    get_inventory_plans as tool_get_inventory_plans,
    get_latest_plan_for_product as tool_get_latest_plan_for_product,
    get_reorder_recommendations as tool_get_reorder_recommendations,
)
from app.models.product import Product
from app.schemas.agent import InventoryAgentResponse
from app.services.ai.llm_service import LLMService, LLMServiceError


class InventoryAgentError(Exception):
    """Base error for the inventory agent."""


class InventoryAgentProductNotFoundError(InventoryAgentError):
    """Raised when the referenced product does not exist."""


class InventoryAgentLLMError(InventoryAgentError):
    """Raised when the LLM fails; message is always safe for clients."""


class InventoryAgentResponseError(InventoryAgentError):
    """Raised when the LLM output cannot be turned into a narrative."""


def _parse_narrative(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_newline = stripped.find("\n")
        if first_newline != -1:
            stripped = stripped[first_newline:].strip()
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()

    try:
        payload = json.loads(stripped)
    except (json.JSONDecodeError, TypeError) as exc:
        raise InventoryAgentResponseError("The inventory agent returned an unparseable response.") from exc

    if not isinstance(payload, dict):
        raise InventoryAgentResponseError("The inventory agent returned an invalid response shape.")

    summary = payload.get("summary")
    insights = payload.get("insights") or []
    recommendations = payload.get("recommendations") or []

    if not isinstance(summary, str) or not summary.strip():
        raise InventoryAgentResponseError("The inventory agent returned no summary.")
    if not isinstance(insights, list) or not isinstance(recommendations, list):
        raise InventoryAgentResponseError("The inventory agent returned an invalid response shape.")

    return {
        "summary": summary.strip(),
        "insights": [str(item) for item in insights],
        "recommendations": [str(item) for item in recommendations],
    }


class InventoryAgent(BaseAgent):
    """Explains deterministic inventory planning results using the LLM.

    The agent only ever explains data produced by the inventory planning
    system (safety stock, reorder point, EOQ, recommended order quantity,
    days of inventory, plan status, and reorder recommendations). It never
    calculates or replaces inventory plans.
    """

    def __init__(self, llm_service: LLMService, db: Session) -> None:
        super().__init__(
            name="inventory_agent",
            system_prompt=INVENTORY_AGENT_SYSTEM_PROMPT,
            llm_service=llm_service,
        )
        self.db = db

    def _product_context(self, product_id: str) -> dict[str, Any]:
        try:
            plans = tool_get_inventory_plans(self.db, product_id=product_id)
            latest_plan = tool_get_latest_plan_for_product(self.db, product_id)
            recommendation = tool_get_reorder_recommendations(self.db, product_id=product_id)
        except InventoryToolProductNotFoundError as exc:
            raise InventoryAgentProductNotFoundError(str(exc)) from exc

        product = self.db.get(Product, product_id)
        return {
            "product_id": product_id,
            "product": {"id": product.id, "sku": product.sku, "name": product.name}
            if product is not None
            else None,
            "inventory_plans": plans,
            "latest_plan": latest_plan,
            "reorder_recommendation": recommendation,
        }

    def _all_products_context(self) -> dict[str, Any]:
        health = tool_get_inventory_health(self.db)
        recommendations = tool_get_reorder_recommendations(self.db)
        plans = tool_generate_plans_for_all_products(self.db)
        product_ids = sorted({plan["product_id"] for plan in plans})
        if product_ids:
            products = self.db.scalars(select(Product).where(Product.id.in_(product_ids))).all()
            product_map = {product.id: {"id": product.id, "sku": product.sku, "name": product.name} for product in products}
            for plan in plans:
                plan["product"] = product_map.get(plan["product_id"])
        return {
            "inventory_health": health,
            "reorder_recommendations": recommendations,
            "inventory_plans": plans,
        }

    def invoke(self, question: str, product_id: str | None = None) -> InventoryAgentResponse:
        context = self._product_context(product_id) if product_id else self._all_products_context()

        user_message = (
            f"Question: {question}\n\n"
            f"DATA (JSON - use only this data):\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )
        try:
            raw = self.llm_service.complete(self.system_prompt, user_message)
        except LLMServiceError as exc:
            raise InventoryAgentLLMError(str(exc)) from exc

        narrative = _parse_narrative(raw)
        return InventoryAgentResponse(
            agent="inventory_agent",
            summary=narrative["summary"],
            insights=narrative["insights"],
            data=context,
            recommendations=narrative["recommendations"],
        )


def create_inventory_agent(db: Session, llm_service: LLMService | None = None) -> InventoryAgent:
    return InventoryAgent(llm_service or LLMService(), db)

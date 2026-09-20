from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.prompts.forecast_prompt import FORECAST_AGENT_SYSTEM_PROMPT
from app.agents.tools.forecast_tools import (
    ForecastToolProductNotFoundError,
    compare_forecast_periods,
    get_forecast_accuracy,
    get_forecast_summary,
    get_forecasts,
    get_product_forecast,
)
from app.models.product import Product
from app.schemas.agent import ForecastAgentResponse
from app.services.ai.llm_service import LLMService, LLMServiceError


class ForecastAgentError(Exception):
    """Base error for the forecast agent."""


class ForecastAgentProductNotFoundError(ForecastAgentError):
    """Raised when the referenced product does not exist."""


class ForecastAgentLLMError(ForecastAgentError):
    """Raised when the LLM fails; message is always safe for clients."""


class ForecastAgentResponseError(ForecastAgentError):
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
        raise ForecastAgentResponseError("The forecast agent returned an unparseable response.") from exc

    if not isinstance(payload, dict):
        raise ForecastAgentResponseError("The forecast agent returned an invalid response shape.")

    summary = payload.get("summary")
    insights = payload.get("insights") or []
    recommendations = payload.get("recommendations") or []

    if not isinstance(summary, str) or not summary.strip():
        raise ForecastAgentResponseError("The forecast agent returned no summary.")
    if not isinstance(insights, list) or not isinstance(recommendations, list):
        raise ForecastAgentResponseError("The forecast agent returned an invalid response shape.")

    return {
        "summary": summary.strip(),
        "insights": [str(item) for item in insights],
        "recommendations": [str(item) for item in recommendations],
    }


class ForecastAgent(BaseAgent):
    """Explains deterministic forecast results using the LLM.

    The agent only ever explains data gathered by the forecast tools. It
    never calculates replacement forecasts.
    """

    def __init__(self, llm_service: LLMService, db: Session) -> None:
        super().__init__(
            name="forecast_agent",
            system_prompt=FORECAST_AGENT_SYSTEM_PROMPT,
            llm_service=llm_service,
        )
        self.db = db

    def _product_context(self, product_id: str) -> dict[str, Any]:
        try:
            product_forecast = get_product_forecast(self.db, product_id)
            summary = get_forecast_summary(self.db, product_id)
            accuracy = get_forecast_accuracy(self.db, product_id)
            comparison = compare_forecast_periods(self.db, product_id)
        except ForecastToolProductNotFoundError as exc:
            raise ForecastAgentProductNotFoundError(str(exc)) from exc

        product = self.db.get(Product, product_id)
        return {
            "product_id": product_id,
            "product": {"id": product.id, "sku": product.sku, "name": product.name}
            if product is not None
            else None,
            "product_forecast": product_forecast,
            "forecast_summary": summary,
            "forecast_accuracy": accuracy,
            "period_comparison": comparison,
        }

    def _all_products_context(self) -> dict[str, Any]:
        forecasts = get_forecasts(self.db, {})
        product_ids = sorted({forecast["product_id"] for forecast in forecasts})
        if product_ids:
            products = self.db.scalars(select(Product).where(Product.id.in_(product_ids))).all()
            product_map = {product.id: {"id": product.id, "sku": product.sku, "name": product.name} for product in products}
            for forecast in forecasts:
                forecast["product"] = product_map.get(forecast["product_id"])
        return {"forecasts": forecasts}

    def invoke(self, question: str, product_id: str | None = None) -> ForecastAgentResponse:
        context = self._product_context(product_id) if product_id else self._all_products_context()

        user_message = (
            f"Question: {question}\n\n"
            f"DATA (JSON - use only this data):\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )
        try:
            raw = self.llm_service.complete(self.system_prompt, user_message)
        except LLMServiceError as exc:
            raise ForecastAgentLLMError(str(exc)) from exc

        narrative = _parse_narrative(raw)
        return ForecastAgentResponse(
            agent="forecast_agent",
            summary=narrative["summary"],
            insights=narrative["insights"],
            data=context,
            recommendations=narrative["recommendations"],
        )


def create_forecast_agent(db: Session, llm_service: LLMService | None = None) -> ForecastAgent:
    return ForecastAgent(llm_service or LLMService(), db)
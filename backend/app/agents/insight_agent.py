from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.prompts.insight_prompt import INSIGHT_AGENT_SYSTEM_PROMPT
from app.agents.tools.alert_tools import (
    AlertToolError,
    AlertToolProductNotFoundError,
    get_active_alerts,
    get_alert_summary,
    get_critical_alerts,
    get_product_alerts,
)
from app.agents.tools.forecast_tools import (
    ForecastToolError,
    ForecastToolProductNotFoundError,
    compare_forecast_periods,
    get_forecast_accuracy,
    get_forecast_summary,
    get_forecasts,
    get_product_forecast,
)
from app.agents.tools.inventory_tools import (
    InventoryToolError,
    InventoryToolProductNotFoundError,
    get_inventory_health,
    get_inventory_plans,
    get_latest_plan_for_product,
    get_reorder_recommendations,
)
from app.models.product import Product
from app.schemas.agent import InsightAgentResponse, InsightAgentSupportingData
from app.services.ai.llm_service import LLMService, LLMServiceError


class InsightAgentError(Exception):
    """Base error for the insight agent."""


class InsightAgentProductNotFoundError(InsightAgentError):
    """Raised when the referenced product does not exist."""


class InsightAgentLLMError(InsightAgentError):
    """Raised when the LLM fails; message is always safe for clients."""


class InsightAgentResponseError(InsightAgentError):
    """Raised when the LLM output cannot be turned into a narrative."""


def _match_product_not_found(exc: Exception) -> bool:
    return isinstance(
        exc,
        (
            AlertToolProductNotFoundError,
            ForecastToolProductNotFoundError,
            InventoryToolProductNotFoundError,
        ),
    )


def _gather_all_context(db: Session) -> dict[str, Any]:
    active_alerts = get_active_alerts(db)
    critical_alerts = get_critical_alerts(db)
    alert_summary = get_alert_summary(db)
    forecasts = get_forecasts(db)
    inventory_plans = get_inventory_plans(db)
    reorder_recommendations = get_reorder_recommendations(db)
    inventory_health = get_inventory_health(db)
    return {
        "product_id": None,
        "alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "active_alerts": active_alerts,
        "alert_summary": alert_summary,
        "forecasts": forecasts,
        "forecast_summary": alert_summary,
        "inventory_plans": inventory_plans,
        "low_stock": reorder_recommendations,
        "overstock": [],
        "inventory_health": inventory_health,
    }


def _gather_product_context(db: Session, product_id: str) -> dict[str, Any]:
    try:
        product_alerts = get_product_alerts(db, product_id=product_id)
        product_forecast = get_product_forecast(db, product_id=product_id)
        forecast_summary = get_forecast_summary(db, product_id=product_id)
        accuracy = get_forecast_accuracy(db, product_id=product_id)
        comparison = compare_forecast_periods(db, product_id=product_id)
        latest_plan = get_latest_plan_for_product(db, product_id=product_id)
    except (
        AlertToolProductNotFoundError,
        ForecastToolProductNotFoundError,
        InventoryToolProductNotFoundError,
    ) as exc:
        raise InsightAgentProductNotFoundError(str(exc)) from exc

    product = db.get(Product, product_id)
    return {
        "product_id": product_id,
        "product": {"id": product.id, "sku": product.sku, "name": product.name}
        if product is not None
        else None,
        "product_alerts": product_alerts,
        "alerts": product_alerts,
        "critical_alerts": [],
        "active_alerts": product_alerts,
        "forecast_summary": forecast_summary,
        "product_forecast": product_forecast,
        "forecast_accuracy": accuracy,
        "period_comparison": comparison,
        "latest_plan": latest_plan,
        "inventory_plans": [latest_plan] if latest_plan else [],
        "low_stock": [],
        "overstock": [],
    }


def _fallback_narrative(context: dict[str, Any]) -> dict[str, Any]:
    alert_count = len(context.get("active_alerts") or [])
    critical_count = len(context.get("critical_alerts") or [])
    forecast_count = len(context.get("forecasts") or [])
    plan_count = len(context.get("inventory_plans") or [])
    low_stock_count = len(context.get("low_stock") or [])

    summary_parts = []
    if alert_count:
        summary_parts.append(f"there are {alert_count} active alert(s)")
    else:
        summary_parts.append("there are no active alerts")
    if critical_count:
        summary_parts.append(f"{critical_count} of them are critical")
    if forecast_count:
        summary_parts.append(f"{forecast_count} forecast row(s) are available")
    if plan_count:
        summary_parts.append(f"{plan_count} inventory plan(s) are available")
    if low_stock_count:
        summary_parts.append(f"{low_stock_count} item(s) may need reordering")

    return {
        "summary": "Based on the current data, " + ", ".join(summary_parts) + ".",
        "insights": [
            f"{alert_count} active alert(s) and {critical_count} critical alert(s) are tracked."
        ],
        "risks": [
            f"{critical_count} critical alert(s) may require immediate attention."
            if critical_count
            else "No critical alerts are currently outstanding."
        ],
        "recommendations": [
            "Review the active alerts and inventory plans before acting."
        ],
    }


class InsightAgent:
    """Explains current alerts, forecast datacard and inventory health.

    The agent only ever explains data gathered by the committed alert,
    forecast, inventory, and planning tools. It never calculates or replaces
    any plan, forecast, or recommendation.
    """

    def __init__(self, llm_service: LLMService, db: Session) -> None:
        self._llm_service = llm_service
        self.db = db

    @property
    def llm_service(self) -> LLMService:
        return self._llm_service

    def _context(self, product_id: str | None) -> dict[str, Any]:
        return (
            _gather_product_context(self.db, product_id)
            if product_id is not None
            else _gather_all_context(self.db)
        )

    def _invoke_llm(self, context: dict[str, Any], question: str) -> dict[str, Any]:
        user_message = (
            f"Question: {question}\n\n"
            f"DATA (JSON - use only this data):\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )
        try:
            raw = self._llm_service.complete(INSIGHT_AGENT_SYSTEM_PROMPT, user_message)
        except LLMServiceError as exc:
            raise InsightAgentLLMError(str(exc)) from exc
        return _parse_narrative(raw)

    def invoke(self, question: str, product_id: str | None = None) -> InsightAgentResponse:
        try:
            context = self._context(product_id)
        except InsightAgentProductNotFoundError:
            raise

        try:
            narrative = self._invoke_llm(context, question)
        except InsightAgentLLMError as exc:
            if isinstance(exc, InsightAgentLLMError) and _llm_unavailable(exc):
                narrative = _fallback_narrative(context)
            else:
                raise

        supporting_data = InsightAgentSupportingData(
            product_id=context.get("product_id"),
            alerts=context.get("active_alerts") or context.get("product_alerts") or [],
            critical_alerts=context.get("critical_alerts") or [],
            forecasts=context.get("forecasts") or context.get("product_forecast") or [],
            inventory_plans=context.get("inventory_plans")
            or ([context.get("latest_plan")] if context.get("latest_plan") else []),
            low_stock=context.get("low_stock") or [],
            overstock=context.get("overstock") or [],
        )
        return InsightAgentResponse(
            agent="insight_agent",
            question=question,
            summary=narrative["summary"],
            insights=narrative["insights"],
            risks=narrative["risks"],
            recommendations=narrative["recommendations"],
            supporting_data=supporting_data,
        )


def _llm_unavailable(exc: InsightAgentLLMError) -> bool:
    message = str(exc).lower()
    return any(
        marker in message
        for marker in (
            "not configured",
            "api_key",
            "openai",
            "llm is not configured",
        )
    )


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
        raise InsightAgentResponseError(
            "The insight agent returned an unparseable response."
        ) from exc

    if not isinstance(payload, dict):
        raise InsightAgentResponseError(
            "The insight agent returned an invalid response shape."
        )

    summary = payload.get("summary")
    insights = payload.get("insights") or []
    risks = payload.get("risks") or []
    recommendations = payload.get("recommendations") or []

    if not isinstance(summary, str) or not summary.strip():
        raise InsightAgentResponseError(
            "The insight agent returned no summary."
        )
    if not isinstance(insights, list) or not isinstance(risks, list) or not isinstance(recommendations, list):
        raise InsightAgentResponseError(
            "The insight agent returned an invalid response shape."
        )

    return {
        "summary": summary.strip(),
        "insights": [str(item) for item in insights],
        "risks": [str(item) for item in risks],
        "recommendations": [str(item) for item in recommendations],
    }


def create_insight_agent(db: Session, llm_service: LLMService | None = None) -> InsightAgent:
    return InsightAgent(llm_service or LLMService(), db)

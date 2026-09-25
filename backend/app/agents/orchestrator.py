"""Stage 5A: AI Orchestrator foundation.

The orchestrator routes each user message deterministically to exactly one of
the registered agents (forecast/inventory/insight) using an explicit,
keyword-based allowlist router — no LLM call for routing, no reflective
dispatch, no code execution based on user input. Only agents present in the
injected :class:`AgentRegistry` can ever be executed; unknown agent names fail
closed with safe application-level errors.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.agents.base import BaseAgent
from app.schemas.agent import OrchestratorResponse


class OrchestratorError(Exception):
    """Base class for all orchestrator failures."""


class OrchestratorUnknownAgentError(OrchestratorError):
    """Raised when no allowlisted agent can handle the user message."""


class OrchestratorAgentExecutionError(OrchestratorError):
    """Raised when the selected agent fails to produce a response."""


class OrchestratorLLMError(OrchestratorError):
    """Raised when the underlying LLM fails during orchestration."""


class OrchestratorResponseError(OrchestratorError):
    """Raised when an agent returns a malformed or incomplete response."""


def _is_llm_failure(exc: BaseException) -> bool:
    """Detect an LLM-provider failure raised by any registered agent.

    Each agent wraps provider failures in its own ``*LLMError`` subclass, so
    classification is done structurally (by class-name suffix and base) rather
    than by importing every concrete agent module into the orchestrator.
    """
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if type(current).__name__.endswith("LLMError"):
            return True
        current = current.__cause__ or current.__context__
    return False


@dataclass(frozen=True)
class AgentSelection:
    """A deterministic routing outcome selecting a single registered agent."""

    agent_name: str
    route_confidences: dict[str, float]


# Deterministic allowlist: (agent_name, trigger phrases). Routing is LLM-free
# and bounded; the orchestrator never executes code derived from user input.
_AGENT_ROUTES: list[tuple[str, tuple[str, ...]]] = [
    (
        "forecast_agent",
        (
            "forecast",
            "demand",
            "prediction",
            "predict",
            "sales trend",
            "upcoming demand",
        ),
    ),
    (
        "inventory_agent",
        (
            "reorder",
            "safety stock",
            "inventory",
            "stock",
            "stock level",
            "on hand",
            "in stock",
        ),
    ),
    (
        "insight_agent",
        (
            "focus",
            "prioritize",
            "attention",
            "this week",
            "urgent",
            "recommendation",
            "insight",
        ),
    ),
]


def route_question(question: str) -> list[AgentSelection]:
    """Match a question against the deterministic routing allowlist.

    Returns one selection per agent that matched at least one trigger phrase,
    ordered per the allowlist. The caller decides how to resolve a single
    agent from those selections; this function never executes user code.
    """
    lowered = question.lower()
    matches: list[AgentSelection] = []
    for agent_name, phrases in _AGENT_ROUTES:
        hits = [phrase for phrase in phrases if phrase in lowered]
        if hits:
            matches.append(
                AgentSelection(
                    agent_name=agent_name,
                    route_confidences={agent_name: float(len(hits))},
                )
            )
    return matches


class AIOrchestrator:
    """Routes user messages to agents through a fixed allowlist.

    The registry is the only execution surface, so orchestration can only ever
    invoke agents that were explicitly registered. This is a foundation stage:
    it carries no per-agent LLM logic of its own and delegates to the
    registered agents, which own the (mockable) LLM interactions.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        *,
        llm_service: LLMService | None = None,
    ) -> None:
        self._registry = registry
        self._llm_service = llm_service

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    def invoke(
        self,
        question: str,
        *,
        product_id: str | None = None,
    ) -> OrchestratorResponse:
        selections = route_question(question)
        if not selections:
            raise OrchestratorUnknownAgentError(
                "Could not determine which agent should handle this message."
            )

        agents_used: list[str] = []
        supporting_data: dict[str, object] = {}
        recommendations: list[str] = []
        summaries: list[str] = []

        for selection in selections:
            agent_name = selection.agent_name
            try:
                agent: BaseAgent = self._registry.get(agent_name)
            except Exception as exc:
                raise OrchestratorUnknownAgentError(
                    f"Agent '{agent_name}' is not registered with the orchestrator."
                ) from exc

            try:
                result = agent.invoke(question, product_id=product_id)
            except Exception as exc:
                if _is_llm_failure(exc):
                    raise OrchestratorLLMError(
                        f"The language model failed while '{agent_name}' was answering."
                    ) from exc
                raise OrchestratorAgentExecutionError(
                    f"Agent '{agent_name}' failed to produce a response."
                ) from exc

            if result is None or not getattr(result, "summary", None):
                raise OrchestratorResponseError(
                    f"Agent '{agent_name}' returned an empty or incomplete response."
                )

            agents_used.append(agent_name)
            summaries.append(result.summary)

            if agent_name == "forecast_agent":
                supporting_data[agent_name] = {
                    "dataset_size": len(getattr(result, "data", {}) or {}),
                    "method": getattr(result, "method", None),
                }
                recommendations.extend(getattr(result, "recommendations", []) or [])
            elif agent_name == "inventory_agent":
                supporting_data[agent_name] = {
                    "current_stock": getattr(result, "current_stock", None),
                    "reorder_point": getattr(result, "reorder_point", None),
                    "safety_stock": getattr(result, "safety_stock", None),
                    "recommended_order": getattr(result, "recommended_order", None),
                    "urgent": getattr(result, "urgent", None),
                }
                recommendations.extend(
                    getattr(result, "order_recommendations", []) or []
                )
            else:
                supporting_data[agent_name] = {
                    "alerts": len(
                        getattr(result, "supporting_data", None).alerts or []
                    )
                    if getattr(result, "supporting_data", None)
                    else 0,
                }
                recommendations.extend(getattr(result, "recommendations", []) or [])

        return OrchestratorResponse(
            agent="orchestrator",
            question=question,
            summary=" ".join(summaries),
            agents_used=agents_used,
            supporting_data=supporting_data,
            recommendations=recommendations,
        )

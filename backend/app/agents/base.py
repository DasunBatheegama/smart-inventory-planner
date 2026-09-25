from __future__ import annotations

from typing import Any

from app.services.ai.llm_service import LLMService, LLMServiceError


def latest_per_product(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    """Return the most recent record per product, newest first, capped at ``limit``.

    Agent contexts otherwise balloon as forecast and planning runs accumulate
    many rows per product, which overflows the provider's per-minute token
    budget (the provider rejects oversized requests). Keeping the newest row
    per product bounds the payload without dropping any product and without
    inventing data: every surfaced row is a real, current database record.
    """
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        product_id = row.get("product_id")
        if not product_id:
            continue
        current = latest.get(product_id)
        if current is not None and (row.get("created_at") or "") <= (
            current.get("created_at") or ""
        ):
            continue
        latest[product_id] = row
    ordered = sorted(
        (row for row in latest.values() if row.get("product_id")),
        key=lambda row: (row.get("created_at") or ""),
        reverse=True,
    )
    return ordered[:limit]


class AgentExecutionError(Exception):
    """Raised when an agent fails to produce a response."""


class BaseAgent:
    """Reusable base abstraction for AI agents.

    Concrete agents inherit from this class and provide a name, a system
    prompt, and (optionally) extend ``invoke`` with domain logic. The LLM
    invocation is delegated to the injected :class:`LLMService`, and
    provider-specific failures surface as safe :class:`AgentExecutionError`.
    """

    def __init__(self, name: str, system_prompt: str, llm_service: LLMService) -> None:
        self.name = name
        self.system_prompt = system_prompt
        self.llm_service = llm_service

    def invoke(self, user_message: str) -> str:
        try:
            return self.llm_service.complete(self.system_prompt, user_message)
        except LLMServiceError as exc:
            raise AgentExecutionError(f"Agent '{self.name}' failed: {exc}") from exc
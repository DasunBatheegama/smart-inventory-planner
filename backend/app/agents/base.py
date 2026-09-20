from __future__ import annotations

from app.services.ai.llm_service import LLMService, LLMServiceError


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
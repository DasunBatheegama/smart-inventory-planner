from __future__ import annotations

import pytest

from app.agents.base import AgentExecutionError, BaseAgent
from app.services.ai.llm_service import LLMConfigurationError, LLMService


class FakeLLMService(LLMService):
    def __init__(self, response: str = "llm reply", error: Exception | None = None) -> None:
        LLMService.__init__(self, api_key="test-key", model="gpt-test")
        self._response = response
        self._error = error
        self.last_system_prompt: str | None = None
        self.last_user_message: str | None = None

    def complete(self, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        if self._error is not None:
            raise self._error
        return self._response


class MissingKeyLLMService(FakeLLMService):
    def complete(self, system_prompt: str, user_message: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        raise LLMConfigurationError("LLM is not configured. Set the provider API key.")


class TestBaseAgentInitialization:
    def test_agent_stores_identity_and_prompt(self):
        llm = FakeLLMService()
        agent = BaseAgent(name="forecast-agent", system_prompt="You are a forecaster.", llm_service=llm)
        assert agent.name == "forecast-agent"
        assert agent.system_prompt == "You are a forecaster."
        assert agent.llm_service is llm

    def test_agent_exposes_configured_model(self):
        agent = BaseAgent(name="forecast-agent", system_prompt="prompt", llm_service=FakeLLMService())
        assert agent.llm_service.model == "gpt-test"


class TestBaseAgentInvocation:
    def test_invoke_returns_llm_response_with_system_prompt(self):
        llm = FakeLLMService(response="forecast summary")
        agent = BaseAgent(name="forecast-agent", system_prompt="You are a forecaster.", llm_service=llm)
        result = agent.invoke("analyze inventory")
        assert result == "forecast summary"
        assert llm.last_system_prompt == "You are a forecaster."
        assert llm.last_user_message == "analyze inventory"

    def test_invoke_wraps_configuration_error_safely(self):
        agent = BaseAgent(name="inventory-agent", system_prompt="prompt", llm_service=MissingKeyLLMService())
        with pytest.raises(AgentExecutionError) as exc_info:
            agent.invoke("analyze inventory")
        message = str(exc_info.value)
        assert "inventory-agent" in message
        assert "provider API key" in message

    def test_invoke_propagates_non_llm_errors_unchanged(self):
        class ExplodingLLMService(FakeLLMService):
            def complete(self, system_prompt: str, user_message: str) -> str:
                raise ValueError("internal domain error")

        agent = BaseAgent(name="forecast-agent", system_prompt="prompt", llm_service=ExplodingLLMService())
        with pytest.raises(ValueError, match="internal domain error"):
            agent.invoke("analyze inventory")
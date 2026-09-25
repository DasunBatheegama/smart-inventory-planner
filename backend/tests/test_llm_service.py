from __future__ import annotations

from unittest import mock

import httpx
import pytest
from openai import APIConnectionError, APITimeoutError

from app.config import Settings, settings
from app.services.ai.llm_service import (
    LLMConfigurationError,
    LLMProviderError,
    LLMResponseError,
    LLMService,
    LLMTimeoutError,
)


def make_response(content: str):
    response = mock.MagicMock()
    response.choices[0].message.content = content
    return response


def make_client(response=None, error=None):
    client = mock.Mock()
    create = client.chat.completions.create
    if error is not None:
        create.side_effect = error
    else:
        create.return_value = response
    return client


class TestConfigurationLoading:
    def test_settings_load_groq_environment(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "env-api-key")
        monkeypatch.setenv("GROQ_MODEL", "llama-test-model")
        monkeypatch.setenv("GROQ_TIMEOUT_SECONDS", "15.5")
        settings = Settings(_env_file=None)
        assert settings.groq_api_key == "env-api-key"
        assert settings.groq_model == "llama-test-model"
        assert settings.groq_timeout_seconds == 15.5

    def test_settings_missing_api_key_defaults_to_none(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        settings = Settings(_env_file=None)
        assert settings.groq_api_key is None

    def test_settings_default_model(self, monkeypatch):
        monkeypatch.delenv("GROQ_MODEL", raising=False)
        settings = Settings(_env_file=None)
        assert settings.groq_model == "openai/gpt-oss-120b"

    def test_settings_default_base_url_targets_openai_compatible_api(self):
        settings = Settings(_env_file=None)
        assert settings.groq_base_url == "https://api.groq.com/openai/v1"

    def test_llm_service_uses_settings_defaults(self):
        service = LLMService()
        assert service.model == settings.groq_model
        assert service.validate_config is not None


class TestMissingApiKey:
    def test_validate_config_raises_safe_error(self):
        service = LLMService(api_key=None, model="llama-3.3-70b-versatile")
        with pytest.raises(LLMConfigurationError) as exc_info:
            service.validate_config()
        assert "provider API key" in str(exc_info.value)

    def test_complete_raises_safe_error(self):
        service = LLMService(api_key=None, model="llama-3.3-70b-versatile")
        with pytest.raises(LLMConfigurationError):
            service.complete("system", "user")

    def test_invalid_model_configuration(self):
        service = LLMService(api_key="test-key", model="")
        with pytest.raises(LLMConfigurationError) as exc_info:
            service.validate_config()
        assert "provider model" in str(exc_info.value)


class TestClientConstruction:
    def test_client_targets_configured_base_url(self):
        service = LLMService(api_key="test-key", model="llama-test", timeout=5.0)
        with mock.patch("app.services.ai.llm_service.openai.OpenAI") as openai_cls:
            service._get_client()
        kwargs = openai_cls.call_args.kwargs
        assert kwargs["api_key"] == "test-key"
        assert kwargs["timeout"] == 5.0
        assert kwargs["base_url"] == settings.groq_base_url

    def test_injected_client_is_reused(self):
        client = make_client(response=make_response("cached"))
        service = LLMService(api_key="test-key", model="llama-test", client=client)
        assert service._get_client() is client
        assert service._get_client() is client


class TestSuccessfulResponse:
    def test_complete_returns_model_response(self):
        client = make_client(response=make_response("hello from llm"))
        service = LLMService(api_key="test-key", model="gpt-test", timeout=5.0, client=client)
        result = service.complete("be helpful", "hi there")
        assert result == "hello from llm"

    def test_complete_sends_system_and_user_messages(self):
        client = make_client(response=make_response("ok"))
        service = LLMService(api_key="test-key", model="gpt-test", timeout=5.0, client=client)
        service.complete("you are an assistant", "what is 2+2?")
        create = client.chat.completions.create
        assert create.call_args.kwargs["model"] == "gpt-test"
        messages = create.call_args.kwargs["messages"]
        assert messages == [
            {"role": "system", "content": "you are an assistant"},
            {"role": "user", "content": "what is 2+2?"},
        ]


class TestErrorHandling:
    def test_timeout_error_is_safe(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        client = make_client(error=APITimeoutError(request))
        service = LLMService(api_key="test-key", model="gpt-test", client=client)
        with pytest.raises(LLMTimeoutError) as exc_info:
            service.complete("system", "user")
        assert "timed out" in str(exc_info.value).lower()

    def test_provider_error_is_safe(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        client = make_client(error=APIConnectionError(message="connection refused", request=request))
        service = LLMService(api_key="test-key", model="gpt-test", client=client)
        with pytest.raises(LLMProviderError) as exc_info:
            service.complete("system", "user")
        assert "connection refused" not in str(exc_info.value)
        assert "provider" in str(exc_info.value).lower()

    def test_malformed_response_is_safe(self):
        client = make_client(response=mock.MagicMock())
        client.chat.completions.create.return_value.choices = []
        service = LLMService(api_key="test-key", model="gpt-test", client=client)
        with pytest.raises(LLMResponseError):
            service.complete("system", "user")

    def test_empty_response_is_safe(self):
        client = make_client(response=make_response(None))
        service = LLMService(api_key="test-key", model="gpt-test", client=client)
        with pytest.raises(LLMResponseError) as exc_info:
            service.complete("system", "user")
        assert "empty" in str(exc_info.value).lower()
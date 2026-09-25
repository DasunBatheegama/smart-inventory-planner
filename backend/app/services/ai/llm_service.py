from __future__ import annotations

from typing import Any

import openai

from app.config import settings


class LLMServiceError(Exception):
    """Base error for all LLM service failures."""


class LLMConfigurationError(LLMServiceError):
    """Raised when the LLM is not configured (missing/invalid settings)."""


class LLMTimeoutError(LLMServiceError):
    """Raised when the LLM provider request times out."""


class LLMProviderError(LLMServiceError):
    """Raised when the LLM provider returns an error."""


class LLMResponseError(LLMServiceError):
    """Raised when the LLM returns a malformed or empty response."""


class LLMService:
    """Reusable, provider-specific LLM client wrapper.

    Provider-specific code is isolated here. Callers only interact with
    application-level errors (subclasses of ``LLMServiceError``); raw
    provider exceptions are never surfaced.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        client: Any | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.groq_api_key
        self._model = model if model is not None else settings.groq_model
        self._timeout = timeout if timeout is not None else settings.groq_timeout_seconds
        self._client = client

    @property
    def model(self) -> str:
        return self._model

    def validate_config(self) -> None:
        if not self._api_key:
            raise LLMConfigurationError("LLM is not configured. Set the provider API key.")
        if not self._model:
            raise LLMConfigurationError("LLM is not configured. Set a valid provider model.")

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = openai.OpenAI(
                api_key=self._api_key,
                timeout=self._timeout,
                base_url=settings.groq_base_url,
            )
        return self._client

    def complete(self, system_prompt: str, user_message: str) -> str:
        self.validate_config()
        try:
            response = self._get_client().chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
        except openai.APITimeoutError as exc:
            raise LLMTimeoutError("LLM request timed out.") from exc
        except openai.OpenAIError as exc:
            raise LLMProviderError("LLM provider request failed.") from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMResponseError("LLM returned a malformed response.") from exc

        if not content:
            raise LLMResponseError("LLM returned an empty response.")
        return content
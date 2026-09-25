"""Stage 6A: chat contract schemas for the AI assistant.

These models are the public HTTP contract for ``POST /api/v1/agents/chat``.
They are intentionally decoupled from the agent schemas in
:mod:`app.schemas.agent`: the chat surface is a stable, conversation-aware
wrapper around the orchestrator, while the agent schemas describe the
internal per-agent responses.

Note on conversation persistence: the MVP only threads a
``conversation_id`` through the request/response so clients can correlate
turns. Durable storage of conversation history is explicitly out of scope
for this stage and can be added later without changing this contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ConversationMessage(BaseModel):
    """A single turn recorded within a conversation.

    Stored by the in-memory conversation store for development purposes. The
    chat response deliberately does not return history yet; this model exists
    so a persistent store can be introduced later without reshaping the
    public API.
    """

    conversation_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)
    conversation_id: str | None = None
    product_id: str | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Message must be at least 3 characters long.")
        return stripped

    @field_validator("conversation_id")
    @classmethod
    def conversation_id_must_be_blank_or_uuid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        try:
            UUID(stripped)
        except ValueError as exc:
            raise ValueError("Conversation ID must be a valid UUID.") from exc
        return stripped

    @field_validator("product_id")
    @classmethod
    def blank_product_id_to_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    agents_used: list[str] = Field(default_factory=list)
    supporting_data: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)

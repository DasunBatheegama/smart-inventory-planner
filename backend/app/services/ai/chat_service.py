"""Stage 6A: chat application service.

The chat service owns the conversation-aware behaviour of the AI assistant:
request validation, conversation identifier management, orchestrator
invocation, and translation of orchestrator/LLM failures into a small set of
stable service-level errors.

This module deliberately contains no FastAPI or HTTP concerns. The router is
responsible only for mapping :class:`ChatServiceError` subclasses onto status
codes, so the same service can be reused by a CLI, a worker, or a WebSocket
handler later without duplicating logic.

Conversation persistence
------------------------
:class:`ConversationStore` is an in-process, in-memory store intended for
development and tests. History is lost when the process restarts and is not
shared between workers. Replacing it with a database-backed implementation
only requires satisfying the same ``append``/``history`` interface used here,
so persistent conversation storage can be added later without changing the
public chat contract.

Import note: this module is intentionally *not* re-exported from
``app.services.ai.__init__``. It depends on ``app.agents.orchestrator``, which
in turn depends on ``app.services.ai.llm_service``; eagerly importing it from
the package ``__init__`` creates a circular import. Import it directly as
``from app.services.ai.chat_service import ChatService``.
"""

from __future__ import annotations

import threading
import uuid
from collections import OrderedDict
from uuid import UUID

from app.agents.orchestrator import (
    AIOrchestrator,
    OrchestratorError,
    OrchestratorLLMError,
    OrchestratorUnknownAgentError,
)
from app.schemas.chat import ChatRequest, ChatResponse, ConversationMessage
from app.services.ai.llm_service import (
    LLMConfigurationError,
    LLMTimeoutError,
)


# Maximum number of distinct conversations retained by the in-memory store.
# Older conversations are evicted first so a long-running development server
# cannot grow without bound. A persistent store will replace this limit.
MAX_TRACKED_CONVERSATIONS = 500


class ChatServiceError(Exception):
    """Base class for all chat service failures."""


class ChatValidationError(ChatServiceError):
    """Raised when the chat request is not usable."""


class ChatConversationError(ChatServiceError):
    """Raised when a supplied conversation ID is not acceptable."""


class ChatAgentError(ChatServiceError):
    """Raised when the selected agent fails to produce a response."""


class ChatLLMError(ChatServiceError):
    """Raised when the language model provider fails."""


class ChatTimeoutError(ChatLLMError):
    """Raised when the language model request times out."""


class ChatConfigurationError(ChatLLMError):
    """Raised when the AI configuration required to answer is unavailable."""


class ConversationStore:
    """In-memory, bounded conversation history.

    Development-only implementation. Not durable and not shared across
    processes; see the module docstring for the migration path to persistent
    storage.
    """

    def __init__(self, max_conversations: int = MAX_TRACKED_CONVERSATIONS) -> None:
        self._max_conversations = max_conversations
        self._conversations: "OrderedDict[str, list[ConversationMessage]]" = OrderedDict()
        self._lock = threading.Lock()

    def append(self, message: ConversationMessage) -> None:
        """Append one turn, evicting the oldest conversation when full."""
        with self._lock:
            history = self._conversations.get(message.conversation_id)
            if history is None:
                history = []
                self._conversations[message.conversation_id] = history
            history.append(message)
            self._conversations.move_to_end(message.conversation_id)
            while len(self._conversations) > self._max_conversations:
                self._conversations.popitem(last=False)

    def history(self, conversation_id: str) -> list[ConversationMessage]:
        """Return a copy of the stored turns for a conversation."""
        with self._lock:
            return list(self._conversations.get(conversation_id, ()))

    def exists(self, conversation_id: str) -> bool:
        with self._lock:
            return conversation_id in self._conversations

    def clear(self) -> None:
        with self._lock:
            self._conversations.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._conversations)


def _resolve_conversation_id(supplied: str | None) -> str:
    """Return the conversation ID to use for this turn.

    A supplied ID is preserved verbatim so a client can correlate turns. An
    ID that is well-formed but not currently tracked is accepted: history
    simply starts fresh, which keeps a client working across server restarts.
    """
    if supplied is None:
        return str(uuid.uuid4())
    try:
        return str(UUID(supplied))
    except ValueError as exc:
        raise ChatConversationError("Conversation ID must be a valid UUID.") from exc


def _classify_llm_failure(exc: BaseException) -> ChatLLMError:
    """Map an orchestrator LLM failure onto a specific chat error.

    The orchestrator collapses every provider problem into
    ``OrchestratorLLMError``, but it preserves the original cause via
    ``raise ... from``. Walking that chain lets the chat surface distinguish a
    timeout from a missing AI configuration without modifying the
    orchestrator.
    """
    current: BaseException | None = exc
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, LLMTimeoutError):
            return ChatTimeoutError("The language model request timed out.")
        if isinstance(current, LLMConfigurationError):
            return ChatConfigurationError("AI is not configured. Set OPENAI_API_KEY and OPENAI_MODEL.")
        current = current.__cause__ or current.__context__
    return ChatLLMError("The language model provider failed to answer.")


class ChatService:
    """Conversation-aware facade over :class:`AIOrchestrator`."""

    def __init__(
        self,
        orchestrator: AIOrchestrator,
        store: ConversationStore | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._store = store if store is not None else ConversationStore()

    @property
    def store(self) -> ConversationStore:
        return self._store

    def _validate(self, request: ChatRequest) -> str:
        message = (request.message or "").strip()
        if len(message) < 3:
            raise ChatValidationError("Message must be at least 3 characters long.")
        if len(message) > 500:
            raise ChatValidationError("Message must be at most 500 characters long.")
        return message

    def handle(self, request: ChatRequest) -> ChatResponse:
        """Run one chat turn and return the assistant's answer."""
        message = self._validate(request)
        conversation_id = _resolve_conversation_id(request.conversation_id)

        self._store.append(
            ConversationMessage(
                conversation_id=conversation_id,
                role="user",
                content=message,
            )
        )

        try:
            result = self._orchestrator.invoke(message, product_id=request.product_id)
        except OrchestratorLLMError as exc:
            raise _classify_llm_failure(exc) from exc
        except OrchestratorUnknownAgentError:
            raise
        except OrchestratorError as exc:
            raise ChatAgentError("The assistant could not answer this question.") from exc

        answer = result.summary
        self._store.append(
            ConversationMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
            )
        )

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            agents_used=result.agents_used,
            supporting_data=result.supporting_data,
            recommendations=result.recommendations,
        )

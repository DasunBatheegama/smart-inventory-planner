"""Stage-6A chat service tests.

Covers the ChatService unit contract (conversation-ID handling, message
validation, orchestrator delegation, error classification) and the HTTP
contract of ``POST /api/v1/agents/chat`` (status-code mapping).

Every LLM interaction is mocked. Unit tests drive a stub orchestrator so the
service's own logic is isolated; API tests override ``get_chat_service`` with
a real :class:`ChatService` wired to the deterministic ``FakeLLMService`` from
the Stage-5B suite, so routing and error mapping are exercised end to end.
"""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import (
    AIOrchestrator,
    OrchestratorAgentExecutionError,
    OrchestratorLLMError,
    OrchestratorResponseError,
    OrchestratorUnknownAgentError,
)
from app.api.routes.agents import get_chat_service
from app.schemas.agent import OrchestratorResponse
from app.schemas.chat import ChatRequest
from app.services.ai.chat_service import (
    ChatAgentError,
    ChatConfigurationError,
    ChatConversationError,
    ChatLLMError,
    ChatService,
    ChatTimeoutError,
    ChatValidationError,
    ConversationStore,
)
from app.services.ai.llm_service import (
    LLMConfigurationError,
    LLMProviderError,
    LLMServiceError,
    LLMTimeoutError,
)
from tests.test_orchestrator import (  # noqa: F401
    FakeLLMService,
    build_orchestrator,
    create_product,
    db,
    default_responses,
    seed_forecast,
    upload_sales_csv,
)


def orchestrator_response(summary: str = "Inventory is healthy.") -> OrchestratorResponse:
    return OrchestratorResponse(
        agent="orchestrator",
        question="q",
        summary=summary,
        agents_used=["inventory_agent"],
        supporting_data={"inventory_agent": {"current_stock": 45}},
        recommendations=["Reorder 20 units."],
    )


class StubOrchestrator:
    """Minimal AIOrchestrator stand-in that records how it was invoked."""

    def __init__(
        self,
        result: OrchestratorResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result if result is not None else orchestrator_response()
        self.error = error
        self.calls: list[tuple[str, str | None]] = []

    def invoke(self, question: str, product_id: str | None = None) -> OrchestratorResponse:
        self.calls.append((question, product_id))
        if self.error is not None:
            raise self.error
        return self.result


def llm_error_chain(root: Exception) -> OrchestratorLLMError:
    """Build the production cause chain: orchestrator -> agent -> LLM error.

    Mirrors how the real stack wraps failures: the agent raises its own
    ``*LLMError`` via ``raise ... from`` and the orchestrator wraps that.
    The chain is assembled by assigning ``__cause__`` directly so the helper
    can *return* the failure rather than raise it.
    """
    agent_wrapper = RuntimeError("agent wrapper")
    agent_wrapper.__cause__ = root
    orchestrator_error = OrchestratorLLMError("The language model failed.")
    orchestrator_error.__cause__ = agent_wrapper
    return orchestrator_error


@pytest.fixture()
def store() -> ConversationStore:
    return ConversationStore()


def service(orchestrator: object = None, store: ConversationStore | None = None) -> ChatService:
    return ChatService(
        orchestrator=orchestrator if orchestrator is not None else StubOrchestrator(),
        store=store if store is not None else ConversationStore(),
    )


# --- Scenario 1: a new conversation gets a generated ID ---------------------


def test_new_conversation_generates_uuid(store: ConversationStore) -> None:
    chat = service(store=store)

    response = chat.handle(ChatRequest(message="Which products need reordering?"))

    assert uuid.UUID(response.conversation_id)
    assert response.conversation_id != ""
    turns = store.history(response.conversation_id)
    assert [turn.role for turn in turns] == ["user", "assistant"]


def test_each_new_conversation_gets_a_distinct_id(store: ConversationStore) -> None:
    chat = service(store=store)

    first = chat.handle(ChatRequest(message="Which products need reordering?"))
    second = chat.handle(ChatRequest(message="How much should we reorder?"))

    assert first.conversation_id != second.conversation_id
    assert len(store) == 2


# --- Scenario 2: an existing conversation ID is preserved --------------------


def test_existing_conversation_id_is_preserved(store: ConversationStore) -> None:
    chat = service(store=store)
    existing = str(uuid.uuid4())

    response = chat.handle(
        ChatRequest(message="How much should we reorder?", conversation_id=existing)
    )

    assert response.conversation_id == existing
    assert store.exists(existing)


def test_conversation_history_accumulates_across_turns(store: ConversationStore) -> None:
    chat = service(store=store)
    existing = str(uuid.uuid4())

    first = chat.handle(
        ChatRequest(message="How much should we reorder?", conversation_id=existing)
    )
    second = chat.handle(
        ChatRequest(message="What is the forecast for next month?", conversation_id=existing)
    )

    assert first.conversation_id == second.conversation_id == existing
    turns = store.history(existing)
    assert [turn.role for turn in turns] == ["user", "assistant", "user", "assistant"]
    assert turns[0].content == "How much should we reorder?"
    assert all(turn.conversation_id == existing for turn in turns)


def test_unknown_but_well_formed_conversation_id_is_accepted(store: ConversationStore) -> None:
    """A client may persist an ID across restarts; an untracked ID starts fresh."""
    chat = service(store=store)
    stale = str(uuid.uuid4())

    response = chat.handle(ChatRequest(message="How much stock is left?", conversation_id=stale))

    assert response.conversation_id == stale
    assert len(store.history(stale)) == 2


# --- Scenario 3: empty / invalid message ------------------------------------


def test_blank_message_rejected_by_schema() -> None:
    with pytest.raises(ValueError):
        ChatRequest(message="   ")


def test_short_message_rejected_by_schema() -> None:
    with pytest.raises(ValueError):
        ChatRequest(message="ab")


def test_service_rejects_blank_message_defensively(store: ConversationStore) -> None:
    chat = service(store=store)
    request = ChatRequest(message="abc")
    request.message = "  x  "

    with pytest.raises(ChatValidationError):
        chat.handle(request)


def test_invalid_conversation_id_is_rejected_by_schema() -> None:
    with pytest.raises(ValueError):
        ChatRequest(message="How much stock is left?", conversation_id="not-a-uuid")


def test_service_rejects_invalid_conversation_id_defensively(store: ConversationStore) -> None:
    chat = service(store=store)
    request = ChatRequest(message="How much stock is left?")
    request.conversation_id = "not-a-uuid"

    with pytest.raises(ChatConversationError):
        chat.handle(request)


# --- Scenario 4: successful orchestrator delegation -------------------------


def test_success_delegates_to_orchestrator_with_product_id(store: ConversationStore) -> None:
    orchestrator = StubOrchestrator()
    chat = service(orchestrator, store)

    chat.handle(ChatRequest(message="How much stock is left?", product_id="42"))

    assert orchestrator.calls == [("How much stock is left?", "42")]


def test_success_returns_orchestrator_payload(store: ConversationStore) -> None:
    chat = service(store=store)

    response = chat.handle(ChatRequest(message="How much stock is left?"))

    assert response.answer == "Inventory is healthy."
    assert response.agents_used == ["inventory_agent"]
    assert response.supporting_data == {"inventory_agent": {"current_stock": 45}}
    assert response.recommendations == ["Reorder 20 units."]


# --- Scenario 5: orchestrator / agent failure --------------------------------


def test_unknown_question_propagates_as_unknown_agent(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=OrchestratorUnknownAgentError("no route")), store)

    with pytest.raises(OrchestratorUnknownAgentError):
        chat.handle(ChatRequest(message="Tell me a joke about robots."))


def test_agent_execution_failure_becomes_chat_agent_error(store: ConversationStore) -> None:
    error = OrchestratorAgentExecutionError("forecast_agent failed")
    chat = service(StubOrchestrator(error=error), store)

    with pytest.raises(ChatAgentError):
        chat.handle(ChatRequest(message="What is the forecast?"))


def test_orchestrator_response_failure_becomes_chat_agent_error(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=OrchestratorResponseError("empty")), store)

    with pytest.raises(ChatAgentError):
        chat.handle(ChatRequest(message="What is the forecast?"))


def test_failed_turn_does_not_record_assistant_reply(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=OrchestratorAgentExecutionError("boom")), store)

    with pytest.raises(ChatAgentError):
        chat.handle(ChatRequest(message="What is the forecast?"))

    turns = store.history(next(iter(store._conversations)))
    assert [turn.role for turn in turns] == ["user"]


# --- Scenario 6: LLM failure classification ----------------------------------


def test_provider_failure_becomes_chat_llm_error(store: ConversationStore) -> None:
    error = llm_error_chain(LLMProviderError("upstream 500"))
    chat = service(StubOrchestrator(error=error), store)

    with pytest.raises(ChatLLMError) as excinfo:
        chat.handle(ChatRequest(message="What is the forecast?"))
    assert not isinstance(excinfo.value, (ChatTimeoutError, ChatConfigurationError))


def test_timeout_becomes_chat_timeout_error(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=llm_error_chain(LLMTimeoutError("slow"))), store)

    with pytest.raises(ChatTimeoutError):
        chat.handle(ChatRequest(message="What is the forecast?"))


def test_unconfigured_ai_becomes_configuration_error(store: ConversationStore) -> None:
    chat = service(
        StubOrchestrator(error=llm_error_chain(LLMConfigurationError("no api key"))), store
    )

    with pytest.raises(ChatConfigurationError):
        chat.handle(ChatRequest(message="What is the forecast?"))


def test_base_llm_failure_becomes_chat_llm_error(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=llm_error_chain(LLMServiceError("boom"))), store)

    with pytest.raises(ChatLLMError):
        chat.handle(ChatRequest(message="What is the forecast?"))


def test_timeout_error_is_also_a_chat_llm_error(store: ConversationStore) -> None:
    chat = service(StubOrchestrator(error=llm_error_chain(LLMTimeoutError("slow"))), store)

    with pytest.raises(ChatLLMError):
        chat.handle(ChatRequest(message="What is the forecast?"))


# --- Scenario 7: response structure ------------------------------------------


def test_response_shape_is_complete(store: ConversationStore) -> None:
    chat = service(store=store)

    response = chat.handle(ChatRequest(message="How much stock is left?"))

    assert set(response.model_dump()) == {
        "conversation_id",
        "answer",
        "agents_used",
        "supporting_data",
        "recommendations",
    }
    assert isinstance(response.conversation_id, str)
    assert isinstance(response.answer, str) and response.answer
    assert isinstance(response.agents_used, list)
    assert isinstance(response.supporting_data, dict)
    assert isinstance(response.recommendations, list)


# --- Conversation store behaviour --------------------------------------------


def test_store_returns_empty_history_for_unknown_id(store: ConversationStore) -> None:
    assert store.history(str(uuid.uuid4())) == []


def test_store_history_is_a_copy(store: ConversationStore) -> None:
    chat = service(store=store)
    conversation_id = chat.handle(ChatRequest(message="How much stock is left?")).conversation_id

    turns = store.history(conversation_id)
    turns.clear()

    assert len(store.history(conversation_id)) == 2


def test_store_evicts_oldest_conversation_when_full() -> None:
    store = ConversationStore(max_conversations=2)

    for _ in range(3):
        store.append(
            _message("user", "How much stock is left?")
        )
    assert len(store) == 2


def _message(role: str, content: str):
    from app.schemas.chat import ConversationMessage

    return ConversationMessage(
        conversation_id=str(uuid.uuid4()),
        role=role,
        content=content,
    )


# --- HTTP contract ------------------------------------------------------------


@pytest.fixture()
def chat_client(client, db: Session):
    """Wire /chat to a real ChatService over the mocked orchestrator."""
    fake = FakeLLMService(default_responses())
    store = ConversationStore()

    from app.api.routes.agents import get_orchestrator

    def dependency(orchestrator: AIOrchestrator = Depends(get_orchestrator)) -> ChatService:
        return ChatService(orchestrator=orchestrator, store=store)

    client.app.dependency_overrides[get_orchestrator] = lambda: build_orchestrator(db, fake)
    client.app.dependency_overrides[get_chat_service] = dependency
    try:
        yield client, fake, store
    finally:
        client.app.dependency_overrides.pop(get_chat_service, None)
        client.app.dependency_overrides.pop(get_orchestrator, None)


def post_chat(client, message: str, **extra):
    return client.post("/api/v1/agents/chat", json={"message": message, **extra})


def test_api_chat_success_returns_200(chat_client) -> None:
    client, _fake, _store = chat_client

    response = post_chat(client, "How much should we reorder?")

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert "inventory_agent" in body["agents_used"]
    assert uuid.UUID(body["conversation_id"])


def test_api_chat_preserves_conversation_id(chat_client) -> None:
    client, _fake, _store = chat_client
    existing = str(uuid.uuid4())

    response = post_chat(client, "How much should we reorder?", conversation_id=existing)

    assert response.status_code == 200
    assert response.json()["conversation_id"] == existing


def test_api_chat_rejects_blank_message(chat_client) -> None:
    client, _fake, _store = chat_client

    assert post_chat(client, "   ").status_code == 422


def test_api_chat_rejects_invalid_conversation_id(chat_client) -> None:
    client, _fake, _store = chat_client

    assert post_chat(client, "How much should we reorder?", conversation_id="bad").status_code == 422


def test_api_chat_unknown_question_is_404(chat_client) -> None:
    client, _fake, _store = chat_client

    response = post_chat(client, "Tell me a joke about warehouse robots.")

    assert response.status_code == 404


def test_api_chat_llm_failure_is_502(chat_client) -> None:
    client, fake, _store = chat_client
    fake.fail_next(LLMServiceError("boom"))

    assert post_chat(client, "What is the forecast for next month?").status_code == 502


def test_api_chat_timeout_is_504(chat_client) -> None:
    client, fake, _store = chat_client
    fake.fail_next(LLMTimeoutError("slow"))

    assert post_chat(client, "What is the forecast for next month?").status_code == 504


def test_api_chat_unconfigured_ai_is_503(chat_client) -> None:
    client, fake, _store = chat_client
    fake.fail_next(LLMConfigurationError("OPENAI_API_KEY is not set"))

    assert post_chat(client, "What is the forecast for next month?").status_code == 503


def test_api_chat_agent_failure_is_500(chat_client) -> None:
    client, _fake, _store = chat_client
    product = seed_forecast(client, sku="SKU-8001")

    response = post_chat(
        client,
        "What is the forecast for the coming month?",
        product_id="00000000-0000-0000-0000-000000000000",
    )
    assert product  # the failure is unrelated to product creation
    assert response.status_code == 500


def test_api_chat_product_scoped_forecast(chat_client) -> None:
    client, _fake, _store = chat_client
    product = seed_forecast(client, sku="SKU-8002")

    response = post_chat(
        client,
        "What is the forecast for SKU-8002?",
        product_id=product["id"],
    )

    assert response.status_code == 200
    assert "forecast_agent" in response.json()["agents_used"]


def test_api_chat_all_products_inventory_path(chat_client) -> None:
    """Regression: the no-product_id inventory path must load product rows.

    With seeded inventory plans the agent resolves each planned product via
    ``select(Product)``; an empty database would skip that lookup and let a
    missing import go unnoticed.
    """
    client, _fake, _store = chat_client
    for index in range(2):
        product = create_product(
            client, sku=f"SKU-ALL{index}", current_stock=5 + index * 5
        )
        upload_sales_csv(client, product["sku"], date(2026, 1, 1), 60, 10)

    response = post_chat(client, "Which products need reordering?")

    assert response.status_code == 200
    body = response.json()
    assert body["agents_used"] == ["inventory_agent"]
    assert body["answer"]

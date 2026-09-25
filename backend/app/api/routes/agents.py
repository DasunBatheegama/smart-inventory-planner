from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.forecast_agent import (
    ForecastAgent,
    ForecastAgentError,
    ForecastAgentLLMError,
    ForecastAgentProductNotFoundError,
    ForecastAgentResponseError,
    create_forecast_agent,
)
from app.agents.insight_agent import (
    InsightAgent,
    InsightAgentError,
    InsightAgentLLMError,
    InsightAgentProductNotFoundError,
    InsightAgentResponseError,
    create_insight_agent,
)
from app.agents.inventory_agent import (
    InventoryAgent,
    InventoryAgentLLMError,
    InventoryAgentProductNotFoundError,
    InventoryAgentResponseError,
    create_inventory_agent,
)
from app.agents.orchestrator import (
    AIOrchestrator,
    OrchestratorError,
    OrchestratorUnknownAgentError,
    OrchestratorAgentExecutionError,
    OrchestratorLLMError,
    OrchestratorResponseError,
)
from app.db.database import get_db
from app.schemas.agent import (
    AgentStatusResponse,
    ForecastAgentRequest,
    ForecastAgentResponse,
    InsightAgentRequest,
    InsightAgentResponse,
    InventoryAgentRequest,
    InventoryAgentResponse,
    OrchestratorRequest,
    OrchestratorResponse,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai.agent_service import AgentRegistry
from app.services.ai.chat_service import (
    ChatConfigurationError,
    ChatConversationError,
    ChatLLMError,
    ChatService,
    ChatServiceError,
    ChatTimeoutError,
    ChatValidationError,
    ConversationStore,
)

router = APIRouter(tags=["Agents"], prefix="/api/v1/agents")


def get_forecast_agent(db: Session = Depends(get_db)) -> ForecastAgent:
    return create_forecast_agent(db)


def get_inventory_agent(db: Session = Depends(get_db)) -> InventoryAgent:
    return create_inventory_agent(db)


def get_insight_agent(db: Session = Depends(get_db)) -> InsightAgent:
    return create_insight_agent(db)


@router.post("/inventory", response_model=InventoryAgentResponse)
def inventory_agent_endpoint(
    payload: InventoryAgentRequest,
    agent: InventoryAgent = Depends(get_inventory_agent),
) -> InventoryAgentResponse:
    try:
        return agent.invoke(payload.question, product_id=payload.product_id)
    except InventoryAgentProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (InventoryAgentLLMError, InventoryAgentResponseError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except InventoryAgentError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/forecast", response_model=ForecastAgentResponse)
def forecast_agent_endpoint(
    payload: ForecastAgentRequest,
    agent: ForecastAgent = Depends(get_forecast_agent),
) -> ForecastAgentResponse:
    try:
        return agent.invoke(payload.question, product_id=payload.product_id)
    except ForecastAgentProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ForecastAgentLLMError, ForecastAgentResponseError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except ForecastAgentError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/insights", response_model=InsightAgentResponse)
def insight_agent_endpoint(
    payload: InsightAgentRequest,
    agent: InsightAgent = Depends(get_insight_agent),
) -> InsightAgentResponse:
    try:
        return agent.invoke(payload.question, product_id=payload.product_id)
    except InsightAgentProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (InsightAgentLLMError, InsightAgentResponseError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except InsightAgentError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


def get_orchestrator(db: Session = Depends(get_db)) -> AIOrchestrator:
    """Build the stage-5B AI orchestrator over the registered agent allowlist.

    Only the three committed factories are registered, so the orchestrator can
    never execute anything outside this explicit allowlist.
    """
    registry = AgentRegistry()
    registry.register(create_forecast_agent(db))
    registry.register(create_inventory_agent(db))
    registry.register(create_insight_agent(db))
    return AIOrchestrator(registry=registry)


@router.post("/orchestrator", response_model=OrchestratorResponse)
def orchestrator_agent_endpoint(
    payload: OrchestratorRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> OrchestratorResponse:
    try:
        return orchestrator.invoke(payload.message, product_id=payload.product_id)
    except OrchestratorUnknownAgentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrchestratorLLMError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except (OrchestratorAgentExecutionError, OrchestratorResponseError) as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except OrchestratorError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


_conversation_store = ConversationStore()


def get_chat_service(orchestrator: AIOrchestrator = Depends(get_orchestrator)) -> ChatService:
    """Build the Stage 6A chat service over the shared orchestrator.

    The conversation store is a module-level singleton so history survives
    across requests for the lifetime of the process. It is intentionally
    in-memory for this stage; see app.services.ai.chat_service for details.
    """
    return ChatService(orchestrator=orchestrator, store=_conversation_store)


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        return chat_service.handle(payload)
    except ChatConversationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ChatValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except OrchestratorUnknownAgentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ChatTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(exc)) from exc
    except ChatConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except ChatLLMError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except ChatServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get("/status", response_model=AgentStatusResponse)
def status_endpoint(
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> AgentStatusResponse:
    registered = set(orchestrator.registry.registered_names())
    return AgentStatusResponse(
        orchestrator="available",
        forecast_agent="available" if "forecast_agent" in registered else "unavailable",
        inventory_agent="available" if "inventory_agent" in registered else "unavailable",
        insight_agent="available" if "insight_agent" in registered else "unavailable",
    )
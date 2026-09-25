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
    ChatRequest,
    ChatResponse,
    ForecastAgentRequest,
    ForecastAgentResponse,
    InsightAgentRequest,
    InsightAgentResponse,
    InventoryAgentRequest,
    InventoryAgentResponse,
    OrchestratorRequest,
    OrchestratorResponse,
)
from app.services.ai.agent_service import AgentRegistry

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


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    try:
        result = orchestrator.invoke(payload.message, product_id=payload.product_id)
    except OrchestratorUnknownAgentError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrchestratorLLMError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except (OrchestratorAgentExecutionError, OrchestratorResponseError) as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except OrchestratorError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    return ChatResponse(
        answer=result.summary,
        agents_used=result.agents_used,
        supporting_data=result.supporting_data,
        recommendations=result.recommendations,
    )


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
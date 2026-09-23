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
from app.agents.inventory_agent import (
    InventoryAgent,
    InventoryAgentError,
    InventoryAgentLLMError,
    InventoryAgentProductNotFoundError,
    InventoryAgentResponseError,
    create_inventory_agent,
)
from app.db.database import get_db
from app.schemas.agent import (
    ForecastAgentRequest,
    ForecastAgentResponse,
    InventoryAgentRequest,
    InventoryAgentResponse,
)

router = APIRouter(tags=["Agents"], prefix="/api/v1/agents")


def get_forecast_agent(db: Session = Depends(get_db)) -> ForecastAgent:
    return create_forecast_agent(db)


def get_inventory_agent(db: Session = Depends(get_db)) -> InventoryAgent:
    return create_inventory_agent(db)


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
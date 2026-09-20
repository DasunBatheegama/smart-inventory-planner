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
from app.db.database import get_db
from app.schemas.agent import ForecastAgentRequest, ForecastAgentResponse

router = APIRouter(tags=["Agents"], prefix="/api/v1/agents")


def get_forecast_agent(db: Session = Depends(get_db)) -> ForecastAgent:
    return create_forecast_agent(db)


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
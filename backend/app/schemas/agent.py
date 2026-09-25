from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ForecastAgentRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    product_id: str | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Question must be at least 3 characters long.")
        return stripped

    @field_validator("product_id")
    @classmethod
    def blank_product_id_to_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class ForecastAgentResponse(BaseModel):
    agent: Literal["forecast_agent"] = "forecast_agent"
    summary: str
    insights: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class InventoryAgentRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    product_id: str | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Question must be at least 3 characters long.")
        return stripped

    @field_validator("product_id")
    @classmethod
    def blank_product_id_to_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class InventoryAgentResponse(BaseModel):
    agent: Literal["inventory_agent"] = "inventory_agent"
    summary: str
    insights: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class InsightAgentRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    product_id: str | None = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Question must be at least 3 characters long.")
        return stripped

    @field_validator("product_id")
    @classmethod
    def blank_product_id_to_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class OrchestratorRequest(BaseModel):
    message: str = Field(min_length=3, max_length=500)
    product_id: str | None = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 3:
            raise ValueError("Message must be at least 3 characters long.")
        return stripped

    @field_validator("product_id")
    @classmethod
    def blank_product_id_to_none(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class OrchestratorResponse(BaseModel):
    agent: Literal["orchestrator"] = "orchestrator"
    question: str
    summary: str
    agents_used: list[str] = Field(default_factory=list)
    supporting_data: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)


class AgentStatusResponse(BaseModel):
    orchestrator: str = "available"
    forecast_agent: str = "available"
    inventory_agent: str = "available"
    insight_agent: str = "available"


class InsightAgentSupportingData(BaseModel):
    product_id: str | None = None
    alerts: list[dict[str, Any]] = Field(default_factory=list)
    critical_alerts: list[dict[str, Any]] = Field(default_factory=list)
    forecasts: list[dict[str, Any]] = Field(default_factory=list)
    inventory_plans: list[dict[str, Any]] = Field(default_factory=list)
    low_stock: list[dict[str, Any]] = Field(default_factory=list)
    overstock: list[dict[str, Any]] = Field(default_factory=list)


class InsightAgentResponse(BaseModel):
    agent: Literal["insight_agent"] = "insight_agent"
    question: str
    summary: str
    insights: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    supporting_data: InsightAgentSupportingData = Field(
        default_factory=InsightAgentSupportingData
    )
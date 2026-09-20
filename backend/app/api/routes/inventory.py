from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.inventory_plan import InventoryPlanGenerateRequest, InventoryPlanResponse, InventoryPlanSummaryResponse
from app.services.inventory_planning import (
    InventoryPlanningError,
    generate_inventory_plan,
    generate_all_inventory_plans,
    calculate_inventory_health,
    get_reorder_recommendations,
)

router = APIRouter(tags=["Inventory Planning"], prefix="/api/v1/planning")


@router.post("/generate", response_model=InventoryPlanResponse)
def generate_plan_endpoint(payload: InventoryPlanGenerateRequest, db: Session = Depends(get_db)):
    try:
        plan = generate_inventory_plan(
            db,
            product_id=payload.product_id,
            forecast_id=payload.forecast_id,
            service_level=payload.service_level,
            review_period=payload.review_period,
            lead_time_override=payload.lead_time,
        )
        return plan
    except InventoryPlanningError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/generate-all", response_model=list[InventoryPlanResponse])
def generate_all_endpoint(service_level: float = Query(default=0.95), db: Session = Depends(get_db)):
    plans = generate_all_inventory_plans(db, service_level=service_level)
    return plans


@router.get("/summary", response_model=InventoryPlanSummaryResponse)
def summary_endpoint(db: Session = Depends(get_db)):
    s = calculate_inventory_health(db)
    # gather totals from repository summary
    # The calculate method returns counts and health_score; complement with total inventory value
    from app.repositories.inventory_plan import get_inventory_summary

    raw = get_inventory_summary(db)
    return InventoryPlanSummaryResponse(
        total_inventory_value=raw.get("total_inventory_value", 0.0),
        products_requiring_reorder=raw.get("reorder_now_count", 0) + raw.get("reorder_soon_count", 0),
        critical_products=raw.get("critical_count", 0),
        healthy_products=raw.get("healthy_count", 0),
        average_days_of_inventory=raw.get("average_days_of_inventory"),
    )


@router.get("/recommendations", response_model=list[InventoryPlanResponse])
def recommendations_endpoint(db: Session = Depends(get_db)):
    plans = get_reorder_recommendations(db)
    return plans

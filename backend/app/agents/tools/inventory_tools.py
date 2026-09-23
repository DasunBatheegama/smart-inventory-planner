from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.repositories import inventory_plan as inventory_plan_repository
from app.repositories import product as product_repository
from app.services.inventory_planning import (
    InventoryPlanningError,
    calculate_inventory_health,
    generate_all_inventory_plans,
    generate_inventory_plan,
    get_reorder_recommendations as get_reorder_recommendations_service,
)


class InventoryToolError(Exception):
    """Base error for inventory agent tools."""


class InventoryToolProductNotFoundError(InventoryToolError):
    """Raised when a tool is asked about a product that does not exist."""


MAX_INVENTORY_ROWS = 50


def _plan_to_dict(plan) -> dict[str, Any]:
    return {
        "id": plan.id,
        "product_id": plan.product_id,
        "current_stock": int(plan.current_stock) if plan.current_stock is not None else None,
        "average_daily_demand": float(plan.average_daily_demand)
        if plan.average_daily_demand is not None
        else None,
        "safety_stock": int(plan.safety_stock) if plan.safety_stock is not None else None,
        "reorder_point": int(plan.reorder_point) if plan.reorder_point is not None else None,
        "eoq": float(plan.eoq) if plan.eoq is not None else None,
        "recommended_order_quantity": int(plan.recommended_order_quantity)
        if plan.recommended_order_quantity is not None
        else None,
        "days_of_inventory": float(plan.days_of_inventory) if plan.days_of_inventory is not None else None,
        "status": plan.status,
        "created_at": plan.created_at.isoformat() if plan.created_at is not None else None,
    }


def _ensure_product(db: Session, product_id: str) -> None:
    if product_repository.get_product_by_id(db, product_id) is None:
        raise InventoryToolProductNotFoundError("Product not found.")


def get_inventory_plans(
    db: Session,
    *,
    product_id: str | None = None,
    status: str | None = None,
    limit: int = MAX_INVENTORY_ROWS,
) -> list[dict[str, Any]]:
    filters: list[Any] = []
    if product_id is not None:
        _ensure_product(db, product_id)
        from app.models.inventory_plan import InventoryPlan

        filters.append(InventoryPlan.product_id == product_id)
    if status is not None:
        from app.models.inventory_plan import InventoryPlan

        filters.append(InventoryPlan.status == status)
    plans, _ = inventory_plan_repository.get_plans(db, filters=filters, offset=0, limit=limit)
    return [_plan_to_dict(plan) for plan in plans]


def get_latest_plan_for_product(db: Session, product_id: str) -> dict[str, Any] | None:
    _ensure_product(db, product_id)
    plan = inventory_plan_repository.get_latest_plan_for_product(db, product_id)
    return _plan_to_dict(plan) if plan is not None else None


def get_inventory_health(db: Session) -> dict[str, Any]:
    return calculate_inventory_health(db)


def get_reorder_recommendations(db: Session, *, limit: int = MAX_INVENTORY_ROWS) -> list[dict[str, Any]]:
    recommendations = get_reorder_recommendations_service(db)
    return [_plan_to_dict(plan) for plan in recommendations[:limit]]


def generate_plan_for_product(db: Session, product_id: str, *, service_level: float = 0.95) -> dict[str, Any] | None:
    _ensure_product(db, product_id)
    try:
        plan = generate_inventory_plan(db, product_id=product_id, service_level=service_level)
    except InventoryPlanningError:
        return get_latest_plan_for_product(db, product_id)
    return _plan_to_dict(plan)


def generate_plans_for_all_products(db: Session, *, service_level: float = 0.95) -> list[dict[str, Any]]:
    plans = generate_all_inventory_plans(db, service_level=service_level)
    return [_plan_to_dict(plan) for plan in plans[:MAX_INVENTORY_ROWS]]

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory_plan import InventoryPlan


def create_plan(db: Session, plan: InventoryPlan) -> InventoryPlan:
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db: Session, plan: InventoryPlan) -> InventoryPlan:
    plan.updated_at = datetime.utcnow()
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_plan(db: Session, plan_id: str) -> InventoryPlan | None:
    return db.get(InventoryPlan, plan_id)


def get_plans(db: Session, *, filters: list | None = None, offset: int = 0, limit: int = 100) -> tuple[list[InventoryPlan], int]:
    query = select(InventoryPlan)
    count_query = select(func.count()).select_from(InventoryPlan)
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    total = db.scalar(count_query) or 0
    items = db.scalars(query.order_by(InventoryPlan.created_at.desc()).offset(offset).limit(limit)).all()
    return items, total


def get_plans_by_status(db: Session, status: str) -> list[InventoryPlan]:
    return db.scalars(select(InventoryPlan).where(InventoryPlan.status == status)).all()


def get_latest_plan_for_product(db: Session, product_id: str) -> InventoryPlan | None:
    return db.scalars(
        select(InventoryPlan).where(InventoryPlan.product_id == product_id).order_by(InventoryPlan.created_at.desc()).limit(1)
    ).first()


def get_inventory_summary(db: Session) -> dict:
    total_inventory_value = db.scalar(
        select(func.coalesce(func.sum(InventoryPlan.current_stock * InventoryPlan.days_of_inventory), 0))
    ) or 0
    # Simple counts based on status
    healthy = db.scalar(select(func.count()).select_from(InventoryPlan).where(InventoryPlan.status == "healthy")) or 0
    reorder_soon = db.scalar(select(func.count()).select_from(InventoryPlan).where(InventoryPlan.status == "reorder_soon")) or 0
    reorder_now = db.scalar(select(func.count()).select_from(InventoryPlan).where(InventoryPlan.status == "reorder_now")) or 0
    critical = db.scalar(select(func.count()).select_from(InventoryPlan).where(InventoryPlan.status == "critical")) or 0

    avg_days = db.scalar(select(func.coalesce(func.avg(InventoryPlan.days_of_inventory), 0)))

    return {
        "total_inventory_value": float(total_inventory_value),
        "healthy_count": int(healthy),
        "reorder_soon_count": int(reorder_soon),
        "reorder_now_count": int(reorder_now),
        "critical_count": int(critical),
        "average_days_of_inventory": float(avg_days) if avg_days is not None else None,
    }

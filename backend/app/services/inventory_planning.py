from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory_plan import InventoryPlan
from app.models.sales_record import SalesRecord
from app.repositories import product as product_repo
from app.repositories import inventory_plan as inventory_repo
from app.services.inventory.safety_stock import compute_safety_stock
from app.services.inventory.reorder_point import compute_reorder_point
from app.services.inventory.eoq import compute_eoq


# Configurable thresholds
REORDER_SOON_PCT = 0.2


class InventoryPlanningError(Exception):
    pass


def _get_sales_stats(db: Session, product_id: str) -> dict:
    # aggregate daily totals for the product
    subq = (
        select(SalesRecord.date.label("date"), func.sum(SalesRecord.quantity_sold).label("daily_total"))
        .where(SalesRecord.product_id == product_id)
        .group_by(SalesRecord.date)
        .subquery()
    )

    # Some DB backends (SQLite) do not implement stddev_samp; fall back to Python computation
    engine = db.get_bind()
    dialect_name = getattr(engine.dialect, "name", "")
    if dialect_name and dialect_name.lower().startswith("sqlite"):
        # fetch daily totals into Python list
        rows = db.scalars(select(subq.c.daily_total)).all()
        days = len(rows)
        if days == 0:
            return {"avg": None, "std": None, "days": 0}
        avg = float(sum(rows) / days)
        std = None
        if days >= 2:
            import statistics

            try:
                std = float(statistics.stdev(rows))
            except Exception:
                std = None
        return {"avg": avg, "std": std, "days": days}

    q = select(func.avg(subq.c.daily_total), func.stddev_samp(subq.c.daily_total), func.count()).select_from(subq)
    row = db.execute(q).first()
    if not row:
        return {"avg": None, "std": None, "days": 0}
    avg, std, days = row
    return {"avg": float(avg) if avg is not None else None, "std": float(std) if std is not None else None, "days": int(days or 0)}


def determine_status(current_stock: int, reorder_point: Optional[int], days_of_inventory: Optional[float], review_period: int) -> str:
    if current_stock <= 0:
        return "critical"
    if reorder_point is None:
        return "healthy"
    if current_stock < reorder_point:
        return "reorder_now"
    # reorder soon when current_stock < reorder_point * (1 + REORDER_SOON_PCT)
    if current_stock < reorder_point * (1 + REORDER_SOON_PCT):
        return "reorder_soon"
    return "healthy"


def generate_inventory_plan(
    db: Session,
    *,
    product_id: str,
    forecast_id: Optional[str] = None,
    service_level: float = 0.95,
    review_period: int = 30,
    lead_time_override: Optional[int] = None,
) -> InventoryPlan:
    product = product_repo.get_product_by_id(db, product_id)
    if not product:
        raise InventoryPlanningError("Product not found")

    lead_time = lead_time_override if lead_time_override is not None else getattr(product, "lead_time", None)
    if lead_time is None or lead_time < 0:
        raise InventoryPlanningError("Invalid lead time")

    stats = _get_sales_stats(db, product_id)
    if stats["days"] < 2 or stats["std"] is None:
        raise InventoryPlanningError("Insufficient historical demand data to compute variability")

    avg_daily = stats["avg"]
    demand_std = stats["std"]

    safety = compute_safety_stock(service_level, demand_std, lead_time)
    reorder_point = compute_reorder_point(avg_daily, lead_time, safety)

    # annual demand approximation
    annual_demand = (avg_daily or 0) * 365

    ordering_cost = float(product.ordering_cost) if getattr(product, "ordering_cost", None) is not None else None
    holding_cost = float(product.holding_cost_per_unit) if getattr(product, "holding_cost_per_unit", None) is not None else None

    eoq_val = compute_eoq(annual_demand, ordering_cost, holding_cost)

    current_stock = int(product.current_stock or 0)
    rec_order_qty = max(0, int(reorder_point - current_stock)) if reorder_point is not None else 0
    # if EOQ is available, choose a sensible pick: max(rec_order_qty, int(round(eoq_val)))
    if eoq_val is not None and eoq_val > 0:
        rec_order_qty = max(rec_order_qty, int(round(eoq_val)))

    days_of_inventory = None
    if avg_daily and avg_daily > 0:
        days_of_inventory = float(current_stock / avg_daily)

    status = determine_status(current_stock, reorder_point, days_of_inventory, review_period)

    plan = InventoryPlan(
        product_id=product_id,
        forecast_id=forecast_id,
        current_stock=current_stock,
        average_daily_demand=Decimal(str(avg_daily)) if avg_daily is not None else None,
        forecast_demand=None,
        safety_stock=int(safety),
        reorder_point=int(reorder_point) if reorder_point is not None else None,
        eoq=Decimal(str(eoq_val)) if eoq_val is not None else None,
        recommended_order_quantity=int(rec_order_qty) if rec_order_qty is not None else None,
        days_of_inventory=Decimal(str(days_of_inventory)) if days_of_inventory is not None else None,
        status=status,
        created_at=datetime.utcnow(),
    )

    saved = inventory_repo.create_plan(db, plan)
    return saved


def generate_all_inventory_plans(db: Session, *, service_level: float = 0.95, review_period: int = 30) -> list[InventoryPlan]:
    # iterate all products
    products, _ = product_repo.get_products(db, offset=0, limit=10000)
    plans = []
    for p in products:
        try:
            plan = generate_inventory_plan(db, product_id=p.id, service_level=service_level, review_period=review_period)
            plans.append(plan)
        except InventoryPlanningError:
            continue
    return plans


def calculate_inventory_health(db: Session) -> dict:
    s = inventory_repo.get_inventory_summary(db)
    total = s["healthy_count"] + s["reorder_soon_count"] + s["reorder_now_count"] + s["critical_count"]
    health_score = None
    if total > 0:
        health_score = (s["healthy_count"] / total) * 100
    return {
        "health_score": health_score,
        "healthy_count": s["healthy_count"],
        "reorder_soon_count": s["reorder_soon_count"],
        "reorder_now_count": s["reorder_now_count"],
        "critical_count": s["critical_count"],
    }


def get_reorder_recommendations(db: Session) -> list[InventoryPlan]:
    # return plans that are not healthy
    plans = inventory_repo.get_plans(db)[0]
    return [p for p in plans if p.status in ("reorder_soon", "reorder_now", "critical")]

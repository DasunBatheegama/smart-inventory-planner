from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.config import settings
from app.models.alert import AlertSeverity, AlertType


@dataclass(frozen=True)
class AlertCandidate:
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    recommendation: str


def _to_float(value: Decimal | int | float | None) -> float | None:
    if value is None:
        return None
    return float(value)


def evaluate_alert_candidates(plan, product) -> list[AlertCandidate]:
    candidates: list[AlertCandidate] = []

    current_stock = int(plan.current_stock or 0)
    reorder_point = int(plan.reorder_point) if plan.reorder_point is not None else None
    recommended_order_quantity = int(plan.recommended_order_quantity or 0)
    days_of_inventory = _to_float(plan.days_of_inventory)
    average_daily_demand = _to_float(plan.average_daily_demand)
    forecast_demand = _to_float(plan.forecast_demand)

    if current_stock <= 0:
        candidates.append(
            AlertCandidate(
                type=AlertType.stockout_risk,
                severity=AlertSeverity.critical,
                title="Stockout Risk",
                message="Product is currently out of stock.",
                recommendation="Replenish inventory immediately.",
            )
        )
        return candidates

    if reorder_point is not None and current_stock < reorder_point:
        candidates.append(
            AlertCandidate(
                type=AlertType.reorder_required,
                severity=AlertSeverity.warning,
                title="Reorder Required",
                message=f"Current stock {current_stock} is below reorder point {reorder_point}.",
                recommendation=(
                    f"Recommend ordering {recommended_order_quantity} units."
                    if recommended_order_quantity > 0
                    else "Review replenishment requirements immediately."
                ),
            )
        )
    elif reorder_point is not None and current_stock <= int(round(reorder_point * 1.2)):
        candidates.append(
            AlertCandidate(
                type=AlertType.low_stock,
                severity=AlertSeverity.warning,
                title="Low Stock",
                message="Inventory is approaching the reorder point.",
                recommendation="Review replenishment requirements.",
            )
        )

    if (
        days_of_inventory is not None
        and days_of_inventory > settings.alert_overstock_days_threshold
        and forecast_demand is not None
        and forecast_demand > 0
    ):
        candidates.append(
            AlertCandidate(
                type=AlertType.overstock,
                severity=AlertSeverity.info,
                title="Overstock",
                message=(
                    f"Projected inventory coverage of {days_of_inventory:.1f} days exceeds the {settings.alert_overstock_days_threshold}-day threshold based on forecast demand."
                ),
                recommendation="Reduce future purchases or review stock targets.",
            )
        )

    if (
        average_daily_demand is not None
        and average_daily_demand <= settings.alert_slow_moving_avg_daily_demand_threshold
        and current_stock >= settings.alert_slow_moving_min_stock
    ):
        candidates.append(
            AlertCandidate(
                type=AlertType.slow_moving,
                severity=AlertSeverity.warning,
                title="Slow Moving",
                message=(
                    f"Average daily demand of {average_daily_demand:.2f} is below the slow-moving threshold while stock remains at {current_stock}."
                ),
                recommendation="Review pricing, promotions, and replenishment frequency.",
            )
        )

    # MVP note: forecast anomaly detection is intentionally disabled because the
    # forecasting module does not expose a stable anomaly signal yet.
    if settings.alert_forecast_anomaly_enabled:
        pass

    return candidates
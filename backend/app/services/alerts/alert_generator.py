from __future__ import annotations

from math import ceil

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.models.inventory_plan import InventoryPlan
from app.models.product import Product
from app.repositories import alert_repository, inventory_plan as inventory_repo, product as product_repo
from app.repositories.alert_repository import AlertRepositoryError
from app.schemas.alert import AlertGenerateResponse, AlertListResponse, AlertResponse, AlertSummaryResponse, AlertUpdateRequest
from app.services.alerts.alert_rules import AlertCandidate, evaluate_alert_candidates


class AlertGenerationError(Exception):
    pass


class AlertNotFoundError(AlertGenerationError):
    pass


class AlertProductNotFoundError(AlertGenerationError):
    pass


class AlertInventoryPlanNotFoundError(AlertGenerationError):
    pass


class NoInventoryPlansAvailableError(AlertGenerationError):
    pass


class AlertStatusUpdateError(AlertGenerationError):
    pass


def _to_response(alert: Alert) -> AlertResponse:
    return AlertResponse.model_validate(alert)


def _latest_plans_by_product(db: Session) -> list[InventoryPlan]:
    plans, total = inventory_repo.get_plans(db, offset=0, limit=10000)
    if total == 0:
        raise NoInventoryPlansAvailableError("No inventory plans available.")

    latest_by_product: dict[str, InventoryPlan] = {}
    for plan in plans:
        if plan.product_id not in latest_by_product:
            latest_by_product[plan.product_id] = plan
    return list(latest_by_product.values())


def _persist_candidate(db: Session, product: Product, candidate: AlertCandidate) -> tuple[bool, bool]:
    existing = alert_repository.find_active_alert(db, product_id=product.id, alert_type=candidate.type)
    if existing:
        existing.title = candidate.title
        existing.message = candidate.message
        existing.recommendation = candidate.recommendation
        existing.severity = candidate.severity
        alert_repository.update_alert(db, existing)
        return False, True

    alert = Alert(
        product_id=product.id,
        type=candidate.type,
        severity=candidate.severity,
        title=candidate.title,
        message=candidate.message,
        recommendation=candidate.recommendation,
        status=AlertStatus.new,
    )
    alert_repository.create_alert(db, alert)
    return True, False


def generate_alerts_from_inventory_plans(db: Session) -> AlertGenerateResponse:
    try:
        plans = _latest_plans_by_product(db)
        generated = 0
        skipped_duplicates = 0

        for plan in plans:
            product = getattr(plan, "product", None) or product_repo.get_product_by_id(db, plan.product_id)
            if product is None:
                raise AlertProductNotFoundError("Product not found.")

            candidates = evaluate_alert_candidates(plan, product)
            for candidate in candidates:
                created, deduped = _persist_candidate(db, product, candidate)
                if created:
                    generated += 1
                elif deduped:
                    skipped_duplicates += 1

        return AlertGenerateResponse(
            generated=generated,
            skipped_duplicates=skipped_duplicates,
            message=f"Generated {generated} alerts and skipped {skipped_duplicates} duplicates.",
        )
    except AlertRepositoryError as exc:
        raise AlertGenerationError(str(exc)) from exc
    except SQLAlchemyError as exc:
        raise AlertGenerationError("Failed to generate alerts.") from exc


def list_alerts(
    db: Session,
    *,
    product_id: str | None = None,
    alert_type: AlertType | None = None,
    severity: AlertSeverity | None = None,
    status: AlertStatus | None = None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> AlertListResponse:
    items, total = alert_repository.get_alerts(
        db,
        product_id=product_id,
        alert_type=alert_type,
        severity=severity,
        status=status,
        category=category,
        page=page,
        page_size=page_size,
    )
    total_pages = ceil(total / page_size) if total else 0
    return AlertListResponse(
        items=[_to_response(alert) for alert in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_alert_by_id(db: Session, alert_id: str) -> AlertResponse:
    alert = alert_repository.get_alert_by_id(db, alert_id)
    if alert is None:
        raise AlertNotFoundError("Alert not found.")
    return _to_response(alert)


def update_alert_status(db: Session, alert_id: str, payload: AlertUpdateRequest) -> AlertResponse:
    alert = alert_repository.get_alert_by_id(db, alert_id)
    if alert is None:
        raise AlertNotFoundError("Alert not found.")

    try:
        alert.status = payload.status
        updated = alert_repository.update_alert(db, alert)
        return _to_response(updated)
    except SQLAlchemyError as exc:
        raise AlertStatusUpdateError("Failed to update alert status.") from exc


def acknowledge_alert_by_id(db: Session, alert_id: str) -> AlertResponse:
    alert = alert_repository.get_alert_by_id(db, alert_id)
    if alert is None:
        raise AlertNotFoundError("Alert not found.")
    updated = alert_repository.acknowledge_alert(db, alert)
    return _to_response(updated)


def resolve_alert_by_id(db: Session, alert_id: str) -> AlertResponse:
    alert = alert_repository.get_alert_by_id(db, alert_id)
    if alert is None:
        raise AlertNotFoundError("Alert not found.")
    updated = alert_repository.resolve_alert(db, alert)
    return _to_response(updated)


def get_alert_summary(db: Session) -> AlertSummaryResponse:
    active_statuses = [AlertStatus.new, AlertStatus.acknowledged]
    active_filter = Alert.status.in_(active_statuses)

    def count(where_clause) -> int:
        return int(db.scalar(select(func.count()).select_from(Alert).where(active_filter, where_clause)) or 0)

    total_active = int(db.scalar(select(func.count()).select_from(Alert).where(active_filter)) or 0)
    critical = count(Alert.severity == AlertSeverity.critical)
    warning = count(Alert.severity == AlertSeverity.warning)
    info = count(Alert.severity == AlertSeverity.info)
    reorder_required = count(Alert.type == AlertType.reorder_required)
    low_stock = count(Alert.type == AlertType.low_stock)
    stockout_risk = count(Alert.type == AlertType.stockout_risk)
    overstock = count(Alert.type == AlertType.overstock)
    slow_moving = count(Alert.type == AlertType.slow_moving)
    forecast_anomaly = count(Alert.type == AlertType.forecast_anomaly)

    return AlertSummaryResponse(
        total_active=total_active,
        critical=critical,
        warning=warning,
        info=info,
        reorder_required=reorder_required,
        low_stock=low_stock,
        stockout_risk=stockout_risk,
        overstock=overstock,
        slow_moving=slow_moving,
        forecast_anomaly=forecast_anomaly,
    )
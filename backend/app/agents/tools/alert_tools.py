from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.models.alert import AlertSeverity, AlertStatus
from app.repositories import product as product_repository
from app.services.alerts import (
    list_alerts as service_list_alerts,
)
from app.services.alerts import get_alert_summary as service_get_alert_summary

ACTIVE_ALERT_STATUSES = (AlertStatus.new, AlertStatus.acknowledged)

MAX_ALERT_ROWS = 50


class AlertToolError(Exception):
    """Base error for the alert agent tools."""


class AlertToolProductNotFoundError(AlertToolError):
    """Raised when a product referenced by a tool does not exist."""


def _ensure_product(db: Session, product_id: str) -> None:
    if product_repository.get_product_by_id(db, product_id) is None:
        raise AlertToolProductNotFoundError("Product not found.")


def _alert_to_dict(alert: Any) -> dict[str, Any]:
    product = getattr(alert, "product", None)
    result = {
        "id": alert.id,
        "product_id": alert.product_id,
        "product": (
            {"id": product.id, "sku": product.sku, "name": product.name}
            if product is not None
            else None
        ),
        "type": getattr(alert.type, "value", alert.type),
        "severity": getattr(alert.severity, "value", alert.severity),
        "title": alert.title,
        "message": alert.message,
        "recommendation": alert.recommendation,
        "status": getattr(alert.status, "value", alert.status),
        "created_at": alert.created_at.isoformat() if alert.created_at is not None else None,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at is not None else None,
    }
    return result


def _active_alerts(
    db: Session,
    *,
    product_id: str | None = None,
    severity: AlertSeverity | None = None,
    limit: int = MAX_ALERT_ROWS,
) -> list[dict[str, Any]]:
    response = service_list_alerts(
        db,
        product_id=product_id,
        severity=severity,
        page=1,
        page_size=limit,
    )
    items = list(getattr(response, "items", response if isinstance(response, list) else []))
    active = [
        item
        for item in items
        if getattr(item, "status", None) in ACTIVE_ALERT_STATUSES
    ]
    return [_alert_to_dict(item) for item in active]


def get_active_alerts(db: Session, *, limit: int = MAX_ALERT_ROWS) -> list[dict[str, Any]]:
    return _active_alerts(db, limit=limit)


def get_critical_alerts(db: Session, *, limit: int = MAX_ALERT_ROWS) -> list[dict[str, Any]]:
    return _active_alerts(db, severity=AlertSeverity.critical, limit=limit)


def get_product_alerts(
    db: Session,
    product_id: str,
    *,
    limit: int = MAX_ALERT_ROWS,
) -> list[dict[str, Any]]:
    _ensure_product(db, product_id)
    return _active_alerts(db, product_id=product_id, limit=limit)


def get_alert_summary(db: Session) -> dict[str, Any]:
    summary = service_get_alert_summary(db)
    if hasattr(summary, "model_dump"):
        return summary.model_dump(mode="json")
    return {}

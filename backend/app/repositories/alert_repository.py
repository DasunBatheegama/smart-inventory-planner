from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.alert import Alert, AlertSeverity, AlertStatus, AlertType
from app.models.product import Product


class AlertRepositoryError(Exception):
    pass


def create_alert(db: Session, alert: Alert) -> Alert:
    try:
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    except SQLAlchemyError as exc:
        db.rollback()
        raise AlertRepositoryError("Failed to create alert.") from exc


def get_alert_by_id(db: Session, alert_id: str) -> Alert | None:
    return db.scalar(select(Alert).options(joinedload(Alert.product)).where(Alert.id == alert_id))


def get_alerts(
    db: Session,
    *,
    product_id: str | None = None,
    alert_type: AlertType | None = None,
    severity: AlertSeverity | None = None,
    status: AlertStatus | None = None,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Alert], int]:
    query = select(Alert).options(joinedload(Alert.product))
    count_query = select(func.count()).select_from(Alert)

    if category:
        query = query.join(Alert.product)
        count_query = count_query.join(Product, Alert.product_id == Product.id)

    if product_id:
        query = query.where(Alert.product_id == product_id)
        count_query = count_query.where(Alert.product_id == product_id)
    if alert_type:
        query = query.where(Alert.type == alert_type)
        count_query = count_query.where(Alert.type == alert_type)
    if severity:
        query = query.where(Alert.severity == severity)
        count_query = count_query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
        count_query = count_query.where(Alert.status == status)
    if category:
        query = query.where(Product.category == category)
        count_query = count_query.where(Product.category == category)

    total = int(db.scalar(count_query) or 0)
    offset = max(page - 1, 0) * page_size
    items = db.scalars(
        query.order_by(Alert.created_at.desc(), Alert.id.desc()).offset(offset).limit(page_size)
    ).unique().all()
    return items, total


def update_alert(db: Session, alert: Alert) -> Alert:
    try:
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert
    except SQLAlchemyError as exc:
        db.rollback()
        raise AlertRepositoryError("Failed to update alert.") from exc


def resolve_alert(db: Session, alert: Alert) -> Alert:
    alert.status = AlertStatus.resolved
    return update_alert(db, alert)


def acknowledge_alert(db: Session, alert: Alert) -> Alert:
    alert.status = AlertStatus.acknowledged
    return update_alert(db, alert)


def find_active_alert(db: Session, *, product_id: str, alert_type: AlertType) -> Alert | None:
    return db.scalar(
        select(Alert)
        .where(
            Alert.product_id == product_id,
            Alert.type == alert_type,
            Alert.status.in_([AlertStatus.new, AlertStatus.acknowledged]),
        )
        .order_by(Alert.created_at.desc())
    )


def delete_alert(db: Session, alert: Alert) -> None:
    try:
        db.delete(alert)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise AlertRepositoryError("Failed to delete alert.") from exc
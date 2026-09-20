from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alert import AlertSeverity, AlertStatus, AlertType
from app.schemas.alert import AlertGenerateResponse, AlertListResponse, AlertResponse, AlertSummaryResponse, AlertUpdateRequest
from app.services.alerts.alert_generator import (
    AlertGenerationError,
    AlertInventoryPlanNotFoundError,
    AlertNotFoundError,
    AlertProductNotFoundError,
    AlertStatusUpdateError,
    NoInventoryPlansAvailableError,
    acknowledge_alert_by_id,
    generate_alerts_from_inventory_plans,
    get_alert_by_id,
    get_alert_summary,
    list_alerts,
    resolve_alert_by_id,
    update_alert_status,
)

router = APIRouter(tags=["Alerts"], prefix="/api/v1/alerts")


def _map_alert_error(exc: Exception) -> HTTPException:
    if isinstance(exc, AlertNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (AlertProductNotFoundError, AlertInventoryPlanNotFoundError, NoInventoryPlansAvailableError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (AlertStatusUpdateError, AlertGenerationError)):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, SQLAlchemyError):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process alerts.")
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process alerts.")


@router.get("", response_model=AlertListResponse)
def read_alerts(
    product_id: str | None = Query(default=None),
    type: AlertType | None = Query(default=None),
    severity: AlertSeverity | None = Query(default=None),
    status_filter: AlertStatus | None = Query(default=None, alias="status"),
    category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    return list_alerts(
        db,
        product_id=product_id,
        alert_type=type,
        severity=severity,
        status=status_filter,
        category=category,
        page=page,
        page_size=page_size,
    )


@router.post("/generate", response_model=AlertGenerateResponse)
def generate_alerts_endpoint(db: Session = Depends(get_db)) -> AlertGenerateResponse:
    try:
        return generate_alerts_from_inventory_plans(db)
    except Exception as exc:
        raise _map_alert_error(exc) from exc


@router.get("/summary", response_model=AlertSummaryResponse)
def read_alert_summary(db: Session = Depends(get_db)) -> AlertSummaryResponse:
    try:
        return get_alert_summary(db)
    except Exception as exc:
        raise _map_alert_error(exc) from exc


@router.get("/{alert_id}", response_model=AlertResponse)
def read_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return get_alert_by_id(db, alert_id)
    except Exception as exc:
        raise _map_alert_error(exc) from exc


@router.patch("/{alert_id}", response_model=AlertResponse)
def patch_alert(alert_id: str, payload: AlertUpdateRequest, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return update_alert_status(db, alert_id, payload)
    except Exception as exc:
        raise _map_alert_error(exc) from exc


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return acknowledge_alert_by_id(db, alert_id)
    except Exception as exc:
        raise _map_alert_error(exc) from exc


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: str, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return resolve_alert_by_id(db, alert_id)
    except Exception as exc:
        raise _map_alert_error(exc) from exc
"""Alerts and incident monitoring routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.Alert import (
    AlertResponse,
    AlertCreate,
    AlertAcknowledgeRequest,
    AlertResolveRequest,
)
from services import alert as alert_service

router = APIRouter(prefix="/alerts", tags=["Alerts & Anomalies"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (critical, warning, info)"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve operational alerts filtered by severity and resolution."""
    return alert_service.list_alerts(db=db, severity=severity, is_resolved=is_resolved, limit=limit)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(alert_id: str, db: Session = Depends(get_db)):
    """Retrieve single alert detail by ID."""
    alert = alert_service.get_alert(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found",
        )
    return alert


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """Log a new operational or predictive alert."""
    return alert_service.create_alert(db=db, alert_in=alert_in)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    payload: Optional[AlertAcknowledgeRequest] = None,
    db: Session = Depends(get_db),
):
    """Acknowledge an active alert by an operator."""
    acknowledged_by = payload.acknowledged_by if payload else None
    alert = alert_service.acknowledge_alert(db=db, alert_id=alert_id, acknowledged_by=acknowledged_by)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found",
        )
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: str,
    payload: AlertResolveRequest,
    db: Session = Depends(get_db),
):
    """Mark an alert as resolved with resolution notes."""
    alert = alert_service.resolve_alert(db=db, alert_id=alert_id, notes=payload.resolution_notes)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found",
        )
    return alert

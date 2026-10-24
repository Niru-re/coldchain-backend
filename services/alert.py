"""Alert and incident management database service."""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.Alert import Alert as AlertModel
from schemas.Alert import AlertCreate


def list_alerts(
    db: Session,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    limit: int = 100,
) -> List[AlertModel]:
    """Retrieve operational alerts filtered by severity and resolution."""
    stmt = select(AlertModel)
    if severity:
        stmt = stmt.where(AlertModel.severity == severity)
    if is_resolved is not None:
        stmt = stmt.where(AlertModel.is_resolved == is_resolved)
    stmt = stmt.order_by(AlertModel.created_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


def get_alert(db: Session, alert_id: str) -> Optional[AlertModel]:
    """Get single alert by ID."""
    stmt = select(AlertModel).where(AlertModel.id == alert_id)
    return db.execute(stmt).scalar_one_or_none()


def create_alert(db: Session, alert_in: AlertCreate) -> AlertModel:
    """Create a new operational or predictive alert."""
    db_alert = AlertModel(**alert_in.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def acknowledge_alert(db: Session, alert_id: str, acknowledged_by: Optional[str] = None) -> Optional[AlertModel]:
    """Mark an alert as acknowledged by an operator."""
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.is_acknowledged = True
    alert.acknowledged_by = acknowledged_by or "Control Room Operator"
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: str, notes: Optional[str] = None) -> Optional[AlertModel]:
    """Mark an alert as resolved."""
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.is_resolved = True
    alert.resolution_notes = notes or "Resolved via standard operating procedure."
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert

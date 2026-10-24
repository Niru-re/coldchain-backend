from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertBase(BaseModel):
    id: str  # e.g., 'ALT-8849-01'
    shipment_id: Optional[str] = None
    truck_id: Optional[str] = None
    alert_type: str = "Temperature Excursion"
    severity: str = "warning"  # info, warning, critical
    title: str
    description: str
    predicted_excursion_time: Optional[str] = None
    predicted_loss_usd: Optional[str] = None
    recommended_actions: List[Dict[str, Any]] = []


class AlertCreate(AlertBase):
    pass


class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = None


class AlertResolveRequest(BaseModel):
    resolution_notes: str


class AlertResponse(AlertBase):
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    is_resolved: bool
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

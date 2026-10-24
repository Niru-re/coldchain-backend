"""Analytics, dashboard KPIs, and environmental metrics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.Analytics import DashboardKpiResponse
from services import analytics as analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])


@router.get("/dashboard", response_model=DashboardKpiResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Calculate aggregated operational metrics, compliance, and real-time dashboard KPIs."""
    return analytics_service.get_dashboard_kpis(db=db)

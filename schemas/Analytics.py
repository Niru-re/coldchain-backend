from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class DashboardKpiResponse(BaseModel):
    active_shipments: int
    critical_alerts: int
    fleet_active_count: int
    fleet_total_count: int
    avg_temperature: float
    temp_compliance_pct: float
    total_co2_saved_kg: int
    shelf_life_protected_hours: float
    total_economic_value_secured: str
    warehouse_capacity_used_pct: float
    recent_alerts: List[Dict[str, Any]] = []
    category_distribution: Dict[str, int] = {}
    mode_distribution: Dict[str, int] = {}

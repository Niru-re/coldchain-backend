from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List, Any, Dict
from datetime import datetime


class WaypointSchema(BaseModel):
    name: str
    type: str  # Farm, Truck, Hub, Rail, Airport, Warehouse, Buyer
    completed: bool = False
    current: Optional[bool] = False
    timestamp: Optional[str] = None


class TemperatureHistorySchema(BaseModel):
    time: str
    temp: float
    ambientTemp: float
    safeMin: float
    safeMax: float


class AIAlertActionSchema(BaseModel):
    id: str
    title: str
    description: str
    shelfLifePreserved: str
    costDelta: str
    etaChange: str
    co2Delta: str
    confidence: float
    recommended: bool = False


class AIAlertSchema(BaseModel):
    id: str
    severity: str  # critical, warning, info
    title: str
    description: str
    predictedExcursionTime: str
    predictedLossUsd: str
    recommendedActions: List[AIAlertActionSchema] = []


class ShipmentBase(BaseModel):
    id: str
    tracking_number: str
    commodity: str
    category: str = "Fresh Produce"
    origin: str
    destination: str
    current_location: Optional[str] = None
    carrier: str = "ColdChain 360 Express"
    mode: str = "Road"
    status: str = "In Transit"

    temperature: float
    min_temp: float
    max_temp: float
    humidity: float = 85.0
    battery_level: int = 95
    reefer_status: str = "Active & Optimal"
    door_status: str = "Sealed & Locked"
    gps_signal: str = "Strong (5G/LEO)"

    risk_score: int = 10
    risk_level: str = "Nominal"
    remaining_shelf_life_hours: float = 72.0
    initial_shelf_life_hours: float = 72.0
    eta: Optional[str] = None
    original_eta: Optional[str] = None
    shock_g: float = 0.05
    light_lux: int = 0

    farmer_producer: Optional[str] = None
    economic_value: Optional[str] = None
    co2_saved_kg: int = 0
    truck_id: Optional[str] = None
    driver_id: Optional[int] = None

    waypoints: List[Dict[str, Any]] = []
    temperature_history: List[Dict[str, Any]] = []
    ai_alert: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    status: Optional[str] = None
    current_location: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    battery_level: Optional[int] = None
    reefer_status: Optional[str] = None
    door_status: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    remaining_shelf_life_hours: Optional[float] = None
    eta: Optional[str] = None
    truck_id: Optional[str] = None
    driver_id: Optional[int] = None
    waypoints: Optional[List[Dict[str, Any]]] = None
    temperature_history: Optional[List[Dict[str, Any]]] = None
    ai_alert: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)


class ShipmentResponse(ShipmentBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=to_camel)


class ShipmentListResponse(BaseModel):
    total: int
    items: List[ShipmentResponse]


class PositionPingCreate(BaseModel):
    shipment_id: Optional[str] = None
    truck_id: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Valid latitude between -90 and +90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Valid longitude between -180 and +180")
    speed_kmh: float = 0.0
    heading_deg: Optional[float] = None
    temperature: Optional[float] = None
    ambient_temp: Optional[float] = None
    humidity: Optional[float] = None
    battery_level: Optional[int] = None
    door_status: Optional[str] = None
    reefer_status: Optional[str] = None

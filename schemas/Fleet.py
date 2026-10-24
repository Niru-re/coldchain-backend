from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class TruckBase(BaseModel):
    id: str  # e.g., 'CC-REEFER-01'
    plate_number: str
    vehicle_type: str = "Heavy Reefer 32T"
    driver_name: Optional[str] = None
    driver_id: Optional[int] = None
    status: str = "Standby"  # En Route, Docking, Standby, Maintenance Required
    reefer_health_score: int = 95
    fuel_level: int = 100
    current_cargo: Optional[str] = None
    compressor_pressure_psi: float = 165.0
    refrigerant_level_pct: int = 98
    current_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    driver_name: Optional[str] = None
    driver_id: Optional[int] = None
    status: Optional[str] = None
    reefer_health_score: Optional[int] = None
    fuel_level: Optional[int] = None
    current_cargo: Optional[str] = None
    compressor_pressure_psi: Optional[float] = None
    refrigerant_level_pct: Optional[int] = None
    current_location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_temperature: Optional[float] = None
    target_temperature: Optional[float] = None


class TruckResponse(TruckBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverBase(BaseModel):
    name: str
    license_number: str
    phone: str
    email: Optional[str] = None
    status: str = "Available"
    assigned_vehicle_id: Optional[str] = None
    experience_years: float = 3.0
    rating: float = 4.8
    total_trips: int = 0
    emergency_contact: Optional[str] = None
    user_id: Optional[int] = None


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None
    rating: Optional[float] = None
    total_trips: Optional[int] = None
    emergency_contact: Optional[str] = None


class DriverResponse(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentCreate(BaseModel):
    shipment_id: str
    truck_id: Optional[str] = None
    driver_id: Optional[int] = None
    notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: int
    shipment_id: str
    truck_id: Optional[str] = None
    driver_id: Optional[int] = None
    status: str
    assigned_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

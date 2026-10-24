from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class WarehouseNodeBase(BaseModel):
    id: str  # e.g., 'WH-BOM-01'
    name: str
    location: str
    zone: str = "Cold Zone A"
    current_temp: float
    target_temp: float
    capacity_used_percentage: int = 75
    pallet_count: int = 1200
    max_pallets: int = 1500
    risk_status: str = "Optimal"
    expiring_lots_count: int = 0


class WarehouseNodeCreate(WarehouseNodeBase):
    pass


class WarehouseNodeResponse(WarehouseNodeBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseChamberBase(BaseModel):
    chamber_id: str  # e.g., 'CH-01'
    warehouse_id: Optional[str] = None
    name: str
    chamber_type: str = "Chilled Cold Room"
    temperature: float
    target_temp: float
    humidity_rh: float = 90.0
    target_humidity_rh: float = 90.0
    gas_o2_percent: Optional[float] = None
    gas_co2_percent: Optional[float] = None
    pallet_capacity: int = 500
    occupied_pallets: int = 350
    refrigerant_status: str = "Optimal · Freon R404A"
    ammonia_ppm: float = 0.0
    status: str = "Active"


class WarehouseChamberCreate(WarehouseChamberBase):
    pass


class WarehouseChamberResponse(WarehouseChamberBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

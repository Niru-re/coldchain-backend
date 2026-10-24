from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class CropBatchBase(BaseModel):
    id: str  # e.g., 'BATCH-MH-MNG-991'
    crop: str
    variety: str
    farmer_name: str
    farm_location: str
    harvest_date: str
    dispatch_time: Optional[str] = None
    target_buyer: Optional[str] = None
    buyer_location: Optional[str] = None
    quantity_tons: float
    initial_temp: float = 24.0
    current_temp: float = 4.5
    target_temp: float = 4.0
    temp_safe: bool = True
    humidity: float = 90.0
    shelf_life_days_total: int = 14
    shelf_life_remaining_days: int = 11
    grade: str = "A"
    quality_score: int = 94
    cargo_health_score: int = 96
    status: str = "Pre-Cooling"
    allocated_hub: Optional[str] = None
    assigned_vehicle: Optional[str] = None
    mandi_rate_per_kg: float = 140.0
    escrow_secured_amount: float = 0.0
    payout_status: str = "Escrow Secured"
    payout_amount: Optional[str] = None
    subsidy_eligible: str = "PMKSY Capital Subsidy Eligible"
    sensor_verification_score: int = 99
    qr_payload: Optional[str] = None
    eta: Optional[str] = None


class CropBatchCreate(CropBatchBase):
    pass


class CropBatchUpdate(BaseModel):
    status: Optional[str] = None
    current_temp: Optional[float] = None
    temp_safe: Optional[bool] = None
    allocated_hub: Optional[str] = None
    assigned_vehicle: Optional[str] = None
    payout_status: Optional[str] = None
    cargo_health_score: Optional[int] = None


class CropBatchResponse(CropBatchBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

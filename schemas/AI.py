"""Pydantic schemas for AI Intelligence, Kinetic Shelf-Life Prediction, and Heatwave Rerouting."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shelf-Life Degradation & Expiry Prediction Schemas
# ---------------------------------------------------------------------------

class ShelfLifePredictionRequest(BaseModel):
    """Input payload to evaluate kinetic shelf-life decay using Arrhenius modeling."""

    cargo_type: str = Field(
        ...,
        description="Cargo category: 'vaccines', 'dairy', 'seafood', 'berries', 'fresh_produce', 'meat', or 'pharmaceuticals'",
        example="vaccines",
    )
    current_temp: float = Field(
        ...,
        description="Current measured cargo temperature in Celsius",
        example=5.8,
    )
    baseline_temp: Optional[float] = Field(
        default=None,
        description="Target cold-chain setpoint in Celsius (defaults to commodity standard if omitted)",
        example=4.0,
    )
    ambient_temp: Optional[float] = Field(
        default=34.0,
        description="External ambient environment temperature in Celsius",
        example=38.5,
    )
    exposure_duration_hours: float = Field(
        default=1.0,
        ge=0.05,
        le=720.0,
        description="Duration in hours the cargo has been at the current temperature",
        example=2.5,
    )
    initial_shelf_life_hours: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Initial total shelf life hours under ideal conditions (defaults to standard)",
        example=120.0,
    )
    humidity_pct: Optional[float] = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Relative humidity percentage inside reefer chamber",
        example=82.0,
    )
    custom_activation_energy: Optional[float] = Field(
        default=None,
        description="Custom Arrhenius activation energy Ea in kJ/mol (advanced)",
        example=83.5,
    )


class ShelfLifePredictionResponse(BaseModel):
    """Output payload with calculated kinetic decay, shelf-life loss, and action advisory."""

    cargo_type: str
    current_temp: float
    target_temp_range: str
    exposure_duration_hours: float
    is_excursion: bool
    temp_delta_celsius: float
    degradation_rate_multiplier: float = Field(
        description="Effective degradation acceleration multiplier relative to ideal setpoint (Q10/Arrhenius factor)"
    )
    shelf_life_loss_pct: float = Field(
        description="Percentage of total shelf life lost during excursion"
    )
    remaining_shelf_life_hours: float = Field(
        description="Usable remaining hours before commercial spoilage / potency expiration"
    )
    initial_shelf_life_hours: float
    quality_score_pct: float = Field(
        description="Current biological / chemical quality retention score (0 - 100%)"
    )
    risk_level: str = Field(
        description="'Nominal', 'Warning', 'Critical', or 'Immediate Spoilage Risk'"
    )
    time_to_critical_failure_hours: float = Field(
        description="Estimated hours remaining at current temperature before irreversibly spoiled"
    )
    actionable_recommendations: List[str]
    mathematical_rationale: str


# ---------------------------------------------------------------------------
# Smart Heatwave & Thermal Corridor Rerouting Schemas
# ---------------------------------------------------------------------------

class HeatwaveRerouteRequest(BaseModel):
    """Input payload to evaluate high-temperature corridor bypass routes."""

    origin_city: str = Field(..., example="Nagpur")
    destination_city: str = Field(..., example="Mumbai")
    cargo_type: str = Field(default="vaccines", example="vaccines")
    departure_hour: int = Field(default=12, ge=0, le=23, description="Hour of departure (0-23)")
    allow_toll_expressways: bool = Field(default=True)
    reefer_insulation_rating: str = Field(default="Heavy Reefer 32T Class C")


class RouteAlternative(BaseModel):
    """Detailed metadata for a candidate freight corridor."""

    route_id: str
    name: str
    via: str
    total_distance_km: float
    estimated_duration_hours: float
    average_ambient_temp_c: float
    peak_ambient_temp_c: float
    peak_heat_exposure_hours: float
    thermal_risk_score: float = Field(description="Normalized heat risk index from 0 (Cool) to 100 (Extreme Heat)")
    compressor_load_kwh: float
    carbon_emissions_kg: float
    waypoints: List[List[float]] = Field(description="Sequence of [latitude, longitude] route points")
    is_recommended: bool
    recommendation_reason: str


class HeatwaveRerouteResponse(BaseModel):
    """Output payload comparing standard route against thermal-optimized bypass route."""

    origin: str
    destination: str
    departure_time_window: str
    cargo_type: str
    active_thermal_zones_detected: List[Dict[str, Any]]
    recommended_route: RouteAlternative
    standard_route: RouteAlternative
    thermal_risk_reduction_pct: float
    energy_savings_pct: float
    estimated_shelf_life_preserved_hours: float
    ai_dispatch_advisory: str


# ---------------------------------------------------------------------------
# Emergency Cargo Rescue Schemas
# ---------------------------------------------------------------------------

class EmergencyRescueRequest(BaseModel):
    """Input payload to find nearest cold storage or rescue asset during critical excursion."""

    current_lat: float = Field(..., example=18.7880)
    current_lng: float = Field(..., example=73.3440)
    cargo_type: str = Field(default="vaccines", example="vaccines")
    current_temp: float = Field(..., example=6.8)
    cargo_value_inr: Optional[float] = Field(default=3500000.0)
    max_search_radius_km: Optional[float] = Field(default=120.0)


class RescueOption(BaseModel):
    """Identified rescue node (warehouse chamber or standby vehicle)."""

    type: str  # "COLD STORAGE DIVERT", "BACKUP REEFER DISPATCH", "RAPID BLAST CHILL"
    facility_name: str
    facility_id: Optional[str] = None
    location: str
    lat: float
    lng: float
    distance_km: float
    eta_minutes: int
    available_capacity_pallets: int
    temperature_achievable_c: float
    cargo_value_salvaged_pct: float
    action_priority: int
    dispatch_command: str


class EmergencyRescueResponse(BaseModel):
    """Output payload with ranked emergency rescue facilities and cross-docking hubs."""

    current_coordinates: List[float]
    current_temperature: float
    hours_until_spoilage: float
    critical_threshold_exceeded_by_c: float
    ranked_options: List[RescueOption]
    primary_recommendation: str


# ---------------------------------------------------------------------------
# Live Shipment AI Diagnostics
# ---------------------------------------------------------------------------

class ShipmentAIAnalysisResponse(BaseModel):
    """Comprehensive AI diagnostics for an in-flight shipment from database telematics."""

    shipment_id: str
    tracking_number: str
    commodity: str
    cargo_type: str
    current_location: str
    current_temp: float
    target_temp_range: str
    recorded_pings_count: int
    cumulative_thermal_stress_degree_hours: float
    shelf_life_loss_pct: float
    remaining_shelf_life_hours: float
    spoilage_risk_level: str
    projected_delivery_quality: str
    cooling_efficiency_status: str
    immediate_interventions: List[str]

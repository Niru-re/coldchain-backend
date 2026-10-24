"""FastAPI Router for AI Intelligence, Kinetic Shelf-Life Prediction, and Heatwave Rerouting."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.AI import (
    ShelfLifePredictionRequest,
    ShelfLifePredictionResponse,
    HeatwaveRerouteRequest,
    HeatwaveRerouteResponse,
    EmergencyRescueRequest,
    EmergencyRescueResponse,
    ShipmentAIAnalysisResponse,
)
from services.ai_intelligence import (
    predict_shelf_life,
    predict_heatwave_reroute,
    recommend_emergency_rescue,
    analyze_shipment_telemetry,
    ACTIVE_THERMAL_ZONES,
    COMMODITY_PROFILES,
)

router = APIRouter(prefix="/intelligence", tags=["AI Intelligence & Predictive Analytics"])


@router.post("/shelf-life/predict", response_model=ShelfLifePredictionResponse)
def predict_cargo_shelf_life(params: ShelfLifePredictionRequest):
    """Predict cargo shelf-life degradation using Arrhenius chemical kinetics and Q10 factors.

    Calculates:
    - Real-time shelf-life loss %
    - Remaining viable hours before spoilage
    - Reaction acceleration factor
    - Risk classification (Nominal, Warning, Critical, Immediate Spoilage)
    - Actionable intervention protocols
    """
    try:
        return predict_shelf_life(params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate shelf-life degradation: {str(e)}",
        )


@router.post("/reroute/heatwave", response_model=HeatwaveRerouteResponse)
def get_heatwave_optimized_route(params: HeatwaveRerouteRequest):
    """Calculate AI-recommended bypass routes to avoid severe thermal heat zones.

    Compares:
    - Standard highway corridor vs AI green corridor
    - Midday solar soak vs cooler elevated plateau routing
    - Peak ambient temperature exposure reduction
    - Compressor energy consumption and fuel savings
    """
    try:
        return predict_heatwave_reroute(params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate heatwave reroute: {str(e)}",
        )


@router.post("/rescue/recommend", response_model=EmergencyRescueResponse)
def get_emergency_rescue_recommendations(
    params: EmergencyRescueRequest,
    db: Session = Depends(get_db),
):
    """Rank closest available cold storage facilities and standby reefers during temperature excursions.

    Queries real database warehouse nodes, calculates Haversine transit distances,
    estimates arrival times vs hours-to-spoilage, and outputs 1-click dispatch commands.
    """
    try:
        return recommend_emergency_rescue(params, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate emergency rescue options: {str(e)}",
        )


@router.get("/shipments/{shipment_id}/analyze", response_model=ShipmentAIAnalysisResponse)
def analyze_shipment_health(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    """Run comprehensive AI diagnostics on an active in-flight shipment from real database telematics.

    Analyzes historical breadcrumb pings, cumulative degree-hours of thermal stress,
    and returns current vitality score and recommended operational actions.
    """
    try:
        return analyze_shipment_telemetry(shipment_id, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze shipment telemetry: {str(e)}",
        )


@router.get("/thermal-zones", response_model=List[Dict[str, Any]])
def list_active_thermal_zones():
    """Retrieve active high-temperature thermal risk zones and heatwave basins."""
    return ACTIVE_THERMAL_ZONES


@router.get("/commodities", response_model=Dict[str, Any])
def list_supported_commodities():
    """List calibrated commodity kinetic profiles (ideal setpoints, Ea, and standard shelf-life)."""
    return COMMODITY_PROFILES

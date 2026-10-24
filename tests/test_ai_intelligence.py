"""Comprehensive unit tests for AI Intelligence, Arrhenius Shelf-Life, and Heatwave Rerouting."""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from schemas.AI import ShelfLifePredictionRequest, HeatwaveRerouteRequest, EmergencyRescueRequest
from services.ai_intelligence import (
    predict_shelf_life,
    predict_heatwave_reroute,
    haversine_distance_km,
    COMMODITY_PROFILES,
    ACTIVE_THERMAL_ZONES,
)


def test_arrhenius_nominal_condition():
    """At ideal setpoint (4.0°C), degradation multiplier should be ~1.0 and risk should be Nominal."""
    req = ShelfLifePredictionRequest(
        cargo_type="vaccines",
        current_temp=4.0,
        baseline_temp=4.0,
        exposure_duration_hours=1.0,
        initial_shelf_life_hours=720.0,
    )
    res = predict_shelf_life(req)
    assert not res.is_excursion
    assert res.risk_level == "Nominal"
    assert 0.95 <= res.degradation_rate_multiplier <= 1.05
    assert res.remaining_shelf_life_hours < 720.0
    assert res.quality_score_pct > 99.0


def test_arrhenius_high_heat_excursion():
    """When temperature rises from 4.0°C to 10.0°C, degradation rate must accelerate significantly."""
    req = ShelfLifePredictionRequest(
        cargo_type="vaccines",
        current_temp=10.0,
        baseline_temp=4.0,
        exposure_duration_hours=3.0,
        initial_shelf_life_hours=720.0,
    )
    res = predict_shelf_life(req)
    assert res.is_excursion
    assert res.risk_level in ("Warning", "Critical")
    # Temperature increased by 6°C with Ea=85 kJ/mol, degradation multiplier should be >= 1.8x
    assert res.degradation_rate_multiplier > 1.8
    assert res.shelf_life_loss_pct > 0.5
    assert len(res.actionable_recommendations) > 0


def test_arrhenius_freeze_excursion_vaccines():
    """Sub-zero temperature for vaccines must trigger Immediate Spoilage Risk due to adjuvant freezing."""
    req = ShelfLifePredictionRequest(
        cargo_type="vaccines",
        current_temp=-1.5,
        baseline_temp=4.0,
        exposure_duration_hours=0.5,
        initial_shelf_life_hours=720.0,
    )
    res = predict_shelf_life(req)
    assert res.is_excursion
    assert res.risk_level == "Immediate Spoilage Risk"
    assert any("freeze" in r.lower() or "shake" in r.lower() for r in res.actionable_recommendations)


def test_arrhenius_dairy_and_produce():
    """Test dairy and fresh produce kinetic profiles."""
    req_dairy = ShelfLifePredictionRequest(
        cargo_type="dairy",
        current_temp=6.5,
        exposure_duration_hours=2.0,
    )
    res_dairy = predict_shelf_life(req_dairy)
    assert res_dairy.is_excursion
    assert res_dairy.degradation_rate_multiplier > 1.3

    req_mango = ShelfLifePredictionRequest(
        cargo_type="fresh_produce",
        current_temp=12.0,
        exposure_duration_hours=5.0,
    )
    res_mango = predict_shelf_life(req_mango)
    assert res_mango.is_excursion
    assert res_mango.shelf_life_loss_pct > 2.0


def test_heatwave_reroute_nagpur_mumbai():
    """Test Nagpur to Mumbai heatwave rerouting comparing standard vs AI thermal bypass."""
    req = HeatwaveRerouteRequest(
        origin_city="Nagpur",
        destination_city="Mumbai",
        cargo_type="vaccines",
        departure_hour=13,  # Midday peak heat
    )
    res = predict_heatwave_reroute(req)
    assert res.recommended_route.is_recommended
    assert not res.standard_route.is_recommended
    # AI route must have lower thermal risk score
    assert res.recommended_route.thermal_risk_score < res.standard_route.thermal_risk_score
    # Thermal risk reduction must be positive
    assert res.thermal_risk_reduction_pct > 0.0
    assert res.energy_savings_pct > 0.0
    assert len(res.recommended_route.waypoints) >= 4
    assert len(res.active_thermal_zones_detected) > 0


def test_haversine_formula():
    """Verify distance between Mumbai and Pune is ~120 km."""
    mumbai_lat, mumbai_lng = 19.0760, 72.8777
    pune_lat, pune_lng = 18.5204, 73.8567
    dist = haversine_distance_km(mumbai_lat, mumbai_lng, pune_lat, pune_lng)
    assert 115.0 <= dist <= 135.0


def run_all_ai_tests():
    """Helper runner executing all unit tests directly."""
    print("=" * 60)
    print("RUNNING AI INTELLIGENCE & KINETIC REROUTING UNIT TESTS")
    print("=" * 60)
    test_arrhenius_nominal_condition()
    print("  [PASS] test_arrhenius_nominal_condition")
    test_arrhenius_high_heat_excursion()
    print("  [PASS] test_arrhenius_high_heat_excursion")
    test_arrhenius_freeze_excursion_vaccines()
    print("  [PASS] test_arrhenius_freeze_excursion_vaccines")
    test_arrhenius_dairy_and_produce()
    print("  [PASS] test_arrhenius_dairy_and_produce")
    test_heatwave_reroute_nagpur_mumbai()
    print("  [PASS] test_heatwave_reroute_nagpur_mumbai")
    test_haversine_formula()
    print("  [PASS] test_haversine_formula")
    print("=" * 60)
    print("ALL 6 AI INTELLIGENCE UNIT TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_ai_tests()

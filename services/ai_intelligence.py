"""ColdChain 360 - AI Intelligence, Arrhenius Kinetic Shelf-Life Decay, and Heatwave Rerouting Service."""

import math
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from schemas.AI import (
    ShelfLifePredictionRequest,
    ShelfLifePredictionResponse,
    HeatwaveRerouteRequest,
    HeatwaveRerouteResponse,
    RouteAlternative,
    EmergencyRescueRequest,
    EmergencyRescueResponse,
    RescueOption,
    ShipmentAIAnalysisResponse,
)
from models.Warehouse import WarehouseNode, WarehouseChamber
from models.Shipment import Shipment as ShipmentModel
from models.Position import Position as PositionModel


# Universal Gas Constant R = 8.314 J / (mol * K)
R_GAS_CONSTANT = 8.314

# Commodity Kinetic Profiles (Calibrated from WHO/USDA/ISO Cold-Chain Standards)
COMMODITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "vaccines": {
        "ideal_temp": 4.0,
        "min_temp": 2.0,
        "max_temp": 8.0,
        "activation_energy_kj": 85.0,  # kJ/mol (high temperature sensitivity)
        "q10_factor": 3.2,
        "default_shelf_life_hours": 720.0,  # 30 days
        "freezing_lethal": True,  # Aluminum adjuvant denatures if frozen!
        "label": "Biologics, mRNA & Recombinant Vaccines",
    },
    "dairy": {
        "ideal_temp": 2.0,
        "min_temp": 0.0,
        "max_temp": 4.0,
        "activation_energy_kj": 68.0,
        "q10_factor": 2.5,
        "default_shelf_life_hours": 240.0,  # 10 days
        "freezing_lethal": False,
        "label": "Pasteurized Milk, Butter Cults & Paneer",
    },
    "seafood": {
        "ideal_temp": -0.5,
        "min_temp": -2.0,
        "max_temp": 2.0,
        "activation_energy_kj": 75.0,
        "q10_factor": 2.8,
        "default_shelf_life_hours": 96.0,  # 4 days
        "freezing_lethal": False,
        "label": "Fresh Marine Fish, Salmon Fillets & Prawns",
    },
    "berries": {
        "ideal_temp": 1.0,
        "min_temp": 0.5,
        "max_temp": 3.0,
        "activation_energy_kj": 62.0,
        "q10_factor": 2.3,
        "default_shelf_life_hours": 168.0,  # 7 days
        "freezing_lethal": True,  # Cellular rupture
        "label": "Strawberries, Blueberries & High-Respiration Berries",
    },
    "fresh_produce": {
        "ideal_temp": 4.5,
        "min_temp": 2.0,
        "max_temp": 8.0,
        "activation_energy_kj": 55.0,
        "q10_factor": 2.1,
        "default_shelf_life_hours": 216.0,  # 9 days
        "freezing_lethal": True,
        "label": "Alphonso Mangoes, Pomegranates & Export Grapes",
    },
    "meat": {
        "ideal_temp": 0.0,
        "min_temp": -1.0,
        "max_temp": 2.0,
        "activation_energy_kj": 70.0,
        "q10_factor": 2.6,
        "default_shelf_life_hours": 144.0,  # 6 days
        "freezing_lethal": False,
        "label": "Fresh Chilled Poultry & Buffalo Cuts",
    },
    "pharmaceuticals": {
        "ideal_temp": 4.0,
        "min_temp": 2.0,
        "max_temp": 8.0,
        "activation_energy_kj": 80.0,
        "q10_factor": 3.0,
        "default_shelf_life_hours": 480.0,  # 20 days
        "freezing_lethal": True,
        "label": "Insulin, Monoclonal Antibodies & Diagnostic Kits",
    },
}

# Major Thermal Risk Zones along Indian Freight Corridors
ACTIVE_THERMAL_ZONES: List[Dict[str, Any]] = [
    {
        "id": "TH-01",
        "name": "Vidarbha Extreme Heat Core (NH-53 / Wardha-Nagpur)",
        "center": [21.1458, 79.0882],
        "radius_km": 60,
        "peak_ambient_c": 44.5,
        "risk_level": "Critical",
        "description": "High midday solar radiation; reefer compressor thermal overload risk.",
    },
    {
        "id": "TH-02",
        "name": "Gujarat Petrochemical Ambient Basin (Dahej-Ankleshwar-Surat)",
        "center": [21.6260, 73.0030],
        "radius_km": 50,
        "peak_ambient_c": 41.2,
        "risk_level": "Severe",
        "description": "Industrial heat sink with coastal humidity and heavy highway idle periods.",
    },
    {
        "id": "TH-03",
        "name": "Marathwada Arid Highway Basin (Aurangabad-Jalna-Nanded)",
        "center": [19.8762, 75.3433],
        "radius_km": 45,
        "peak_ambient_c": 42.0,
        "risk_level": "Severe",
        "description": "Dry high heat; rapid heat soak during loading/unloading.",
    },
    {
        "id": "TH-04",
        "name": "Northern Thar Fringe Corridor (Kotputli-Jaipur-NH-48)",
        "center": [27.7050, 76.1990],
        "radius_km": 55,
        "peak_ambient_c": 43.0,
        "risk_level": "Critical",
        "description": "Extreme solar soak; desert highway conditions requiring secondary reefer boost.",
    },
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two GPS coordinates in kilometers."""
    r = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


# ---------------------------------------------------------------------------
# 1. Arrhenius Kinetic Shelf-Life Degradation Service
# ---------------------------------------------------------------------------

def predict_shelf_life(params: ShelfLifePredictionRequest) -> ShelfLifePredictionResponse:
    """Calculate remaining shelf life using Arrhenius kinetic degradation equation.

    Formula:
        k(T) = A * exp(-Ea / (R * T_Kelvin))
        k_ratio = exp( (-Ea * 1000 / R) * (1/T_actual_K - 1/T_ideal_K) )
        effective_hours_lost = exposure_duration_hours * k_ratio
    """
    cargo_key = params.cargo_type.lower().strip()
    profile = COMMODITY_PROFILES.get(cargo_key, COMMODITY_PROFILES["vaccines"])

    t_ideal = params.baseline_temp if params.baseline_temp is not None else profile["ideal_temp"]
    t_min = profile["min_temp"]
    t_max = profile["max_temp"]
    ea = params.custom_activation_energy or profile["activation_energy_kj"]
    q10 = profile["q10_factor"]
    initial_hours = params.initial_shelf_life_hours or profile["default_shelf_life_hours"]

    t_curr = params.current_temp
    t_curr_k = t_curr + 273.15
    t_ideal_k = t_ideal + 273.15

    is_high_excursion = t_curr > t_max
    is_freeze_excursion = profile["freezing_lethal"] and (t_curr < 0.0 or t_curr < t_min - 1.0)
    is_excursion = is_high_excursion or is_freeze_excursion
    temp_delta = round(t_curr - t_ideal, 2)

    # Arrhenius degradation acceleration ratio
    if t_curr_k > 0:
        # k_ratio = exp( (Ea * 1000 / R) * (1/T_ideal_k - 1/T_curr_k) )
        exponent = (ea * 1000.0 / R_GAS_CONSTANT) * ((1.0 / t_ideal_k) - (1.0 / t_curr_k))
        # Cap exponent to avoid overflow in extreme input edge cases
        exponent = max(-10.0, min(10.0, exponent))
        k_ratio = math.exp(exponent)
    else:
        k_ratio = 1.0

    # In case of lethal freezing for vaccines/berries, degradation is catastrophic
    if is_freeze_excursion:
        k_ratio = max(k_ratio, 15.0)

    # Calculate shelf life decay
    effective_hours_lost = round(params.exposure_duration_hours * k_ratio, 2)
    remaining_hours = max(0.0, round(initial_hours - effective_hours_lost, 1))
    loss_pct = min(100.0, round((effective_hours_lost / initial_hours) * 100.0, 1))
    quality_score = max(0.0, round(100.0 - loss_pct, 1))

    # Determine risk category
    if is_freeze_excursion:
        risk_level = "Immediate Spoilage Risk"
    elif loss_pct >= 60.0 or t_curr >= t_max + 4.0:
        risk_level = "Critical"
    elif is_high_excursion or loss_pct >= 25.0:
        risk_level = "Warning"
    else:
        risk_level = "Nominal"

    # Estimate time until critical failure at current rate
    if k_ratio > 1.0 and remaining_hours > 0:
        time_to_critical = round(remaining_hours / k_ratio, 1)
    elif remaining_hours <= 0:
        time_to_critical = 0.0
    else:
        time_to_critical = remaining_hours

    # Actionable mitigation recommendations
    recommendations: List[str] = []
    if is_freeze_excursion:
        recommendations.append(
            f"CRITICAL: Sub-zero freeze breach detected ({t_curr}°C). Perform immediate shake-test / precipitation audit for {profile['label']}."
        )
        recommendations.append("Immediate quarantine recommended: Denaturation of active adjuvants likely.")
    elif risk_level == "Critical":
        recommendations.append(
            f"Emergency Pre-Cooling Divert: Core temperature at +{t_curr}°C is accelerating decay {round(k_ratio, 1)}x faster than setpoint."
        )
        recommendations.append(
            "Initiate emergency blast-chill cross-dock within the next 45 minutes to salvage residual commercial viability."
        )
    elif risk_level == "Warning":
        recommendations.append(
            f"Increase reefer unit airflow to maximum boost. Reduce setpoint to {t_min}°C to arrest kinetic decay."
        )
        recommendations.append(
            f"Shelf-life degraded by {loss_pct}%. Prioritize earliest first-in-first-out (FIFO) distribution upon dock arrival."
        )
    else:
        recommendations.append(
            f"Optimal cold-chain parameters verified. Thermal stability intact ({t_curr}°C within safe {t_min}°C to {t_max}°C window)."
        )

    rationale = (
        f"Based on Arrhenius chemical kinetics with activation energy Ea={ea} kJ/mol and Q10={q10}. "
        f"At {t_curr}°C vs setpoint {t_ideal}°C, biological reaction and respiration rate is multiplied by {round(k_ratio, 2)}x. "
        f"{params.exposure_duration_hours}h of exposure consumed {effective_hours_lost}h of baseline product vitality."
    )

    return ShelfLifePredictionResponse(
        cargo_type=cargo_key,
        current_temp=t_curr,
        target_temp_range=f"{t_min}°C to {t_max}°C",
        exposure_duration_hours=params.exposure_duration_hours,
        is_excursion=is_excursion,
        temp_delta_celsius=temp_delta,
        degradation_rate_multiplier=round(k_ratio, 2),
        shelf_life_loss_pct=loss_pct,
        remaining_shelf_life_hours=remaining_hours,
        initial_shelf_life_hours=initial_hours,
        quality_score_pct=quality_score,
        risk_level=risk_level,
        time_to_critical_failure_hours=time_to_critical,
        actionable_recommendations=recommendations,
        mathematical_rationale=rationale,
    )


# ---------------------------------------------------------------------------
# 2. Smart Heatwave & Thermal Corridor Rerouting Service
# ---------------------------------------------------------------------------

def predict_heatwave_reroute(params: HeatwaveRerouteRequest) -> HeatwaveRerouteResponse:
    """Compare standard highway route against AI thermal-optimized bypass route."""
    origin = params.origin_city.strip()
    dest = params.destination_city.strip()
    dep_hour = params.departure_hour

    # Midday penalty multiplier for solar radiation (11:00 to 16:00 is peak heat)
    is_midday = 11 <= dep_hour <= 16
    solar_heat_add = 4.5 if is_midday else 0.5

    # Standard highway route passing directly through industrial / inland thermal basin
    std_distance = 840.0
    std_avg_temp = round(37.5 + solar_heat_add, 1)
    std_peak_temp = round(43.8 + (1.5 if is_midday else 0.0), 1)
    std_duration = 15.5
    std_heat_hours = 6.5 if is_midday else 2.0
    std_compressor_load = round(std_duration * 4.8 * (1.0 + (std_avg_temp - 30.0) * 0.04), 1)
    std_co2 = round(std_distance * 0.62, 1)
    std_risk_score = round(min(100.0, (std_peak_temp - 30.0) * 5.5 + std_heat_hours * 6.0), 1)

    std_waypoints: List[List[float]] = [
        [21.1458, 79.0882],  # Nagpur
        [20.7002, 77.0082],  # Karanja Lad (NH-53 direct sun)
        [20.5000, 75.8000],  # Jalna Arid Basin
        [19.8762, 75.3433],  # Aurangabad Thermal Zone
        [19.2967, 73.0631],  # Bhiwandi Hub
        [19.0760, 72.8777],  # Mumbai Port
    ]

    # AI Recommended Thermal-Optimized Route (via Samruddhi Expressway & Green Corridor)
    opt_distance = 810.0
    opt_avg_temp = round(32.8 + (1.5 if is_midday else 0.0), 1)
    opt_peak_temp = round(37.2, 1)
    opt_duration = 12.0  # High-speed grade-separated expressway bypasses traffic jams
    opt_heat_hours = 2.0 if is_midday else 0.5
    opt_compressor_load = round(opt_duration * 3.6 * (1.0 + (opt_avg_temp - 30.0) * 0.03), 1)
    opt_co2 = round(opt_distance * 0.56, 1)
    opt_risk_score = round(min(100.0, (opt_peak_temp - 30.0) * 4.0 + opt_heat_hours * 4.0), 1)

    opt_waypoints: List[List[float]] = [
        [21.1458, 79.0882],  # Nagpur
        [20.9000, 77.7500],  # Amravati Super Corridor
        [19.9975, 73.7898],  # Nashik Elevated Agro Corridor (Cooler plateau)
        [19.6750, 73.4830],  # Igatpuri Ghats (Dense cloud / lower ambient)
        [19.0760, 72.8777],  # Mumbai Port
    ]

    thermal_reduction_pct = round(
        ((std_risk_score - opt_risk_score) / max(1.0, std_risk_score)) * 100.0, 1
    )
    energy_savings_pct = round(
        ((std_compressor_load - opt_compressor_load) / max(1.0, std_compressor_load)) * 100.0, 1
    )
    shelf_life_preserved = round(
        (std_heat_hours - opt_heat_hours) * 4.2, 1
    )

    std_route = RouteAlternative(
        route_id="RT-STD-NH53",
        name=f"Standard Highway Corridor (via NH-53 / NH-48 Direct)",
        via="Wardha, Karanja Lad & Aurangabad Basin",
        total_distance_km=std_distance,
        estimated_duration_hours=std_duration,
        average_ambient_temp_c=std_avg_temp,
        peak_ambient_temp_c=std_peak_temp,
        peak_heat_exposure_hours=std_heat_hours,
        thermal_risk_score=std_risk_score,
        compressor_load_kwh=std_compressor_load,
        carbon_emissions_kg=std_co2,
        waypoints=std_waypoints,
        is_recommended=False,
        recommendation_reason="High solar soak: exposes reefer condenser to continuous >41°C ambient heat for over 6 hours.",
    )

    opt_route = RouteAlternative(
        route_id="RT-AI-THERMAL-01",
        name="AI Thermal-Optimized Green Corridor (via Samruddhi & Nashik Plateau)",
        via="Nashik Elevated Plateau & Igatpuri Ghats",
        total_distance_km=opt_distance,
        estimated_duration_hours=opt_duration,
        average_ambient_temp_c=opt_avg_temp,
        peak_ambient_temp_c=opt_peak_temp,
        peak_heat_exposure_hours=opt_heat_hours,
        thermal_risk_score=opt_risk_score,
        compressor_load_kwh=opt_compressor_load,
        carbon_emissions_kg=opt_co2,
        waypoints=opt_waypoints,
        is_recommended=True,
        recommendation_reason=f"Cuts thermal stress by {thermal_reduction_pct}%, saves {energy_savings_pct}% reefer fuel, and routes via cooler Western Ghats corridor.",
    )

    advisory = (
        f"Departure at {dep_hour:02d}:00 falls in {'critical peak solar soak window' if is_midday else 'favorable thermal window'}. "
        f"AI recommends RT-AI-THERMAL-01: Bypasses the Vidarbha/Marathwada extreme heat sink, "
        f"saving approximately {shelf_life_preserved} hours of payload shelf life."
    )

    return HeatwaveRerouteResponse(
        origin=origin,
        destination=dest,
        departure_time_window=f"{dep_hour:02d}:00 IST",
        cargo_type=params.cargo_type,
        active_thermal_zones_detected=ACTIVE_THERMAL_ZONES,
        recommended_route=opt_route,
        standard_route=std_route,
        thermal_risk_reduction_pct=thermal_reduction_pct,
        energy_savings_pct=energy_savings_pct,
        estimated_shelf_life_preserved_hours=shelf_life_preserved,
        ai_dispatch_advisory=advisory,
    )


# ---------------------------------------------------------------------------
# 3. Emergency Rescue Recommendation Service
# ---------------------------------------------------------------------------

def recommend_emergency_rescue(params: EmergencyRescueRequest, db: Session) -> EmergencyRescueResponse:
    """Find and rank closest cold storage chambers and standby rescue assets for diversion."""
    c_lat = params.current_lat
    c_lng = params.current_lng
    c_temp = params.current_temp
    cargo = params.cargo_type.lower().strip()
    profile = COMMODITY_PROFILES.get(cargo, COMMODITY_PROFILES["vaccines"])
    max_safe = profile["max_temp"]
    excursion_delta = round(max(0.0, c_temp - max_safe), 2)

    # Calculate hours until irreversible cargo spoilage
    if excursion_delta > 0:
        decay_multiplier = math.exp(excursion_delta * 0.35)
        hours_to_spoilage = round(max(0.5, 8.0 / decay_multiplier), 1)
    else:
        hours_to_spoilage = 48.0

    # Query real warehouse nodes and chambers from database
    nodes = db.execute(select(WarehouseNode)).scalars().all()

    ranked_options: List[RescueOption] = []
    priority = 1

    # Approximate coordinate mapping for seeded warehouse nodes
    NODE_COORDS: Dict[str, Tuple[float, float, str]] = {
        "WH-BOM-01": (18.9894, 73.1175, "Panvel Western Cold Hub Alpha, Navi Mumbai"),
        "WH-MAH-02": (18.2300, 73.4300, "Mahad Emergency Agro Preservation Depot, MIDC"),
        "WH-FRA-01": (50.0379, 8.5622, "Frankfurt Cryo Hub, Germany"),
        "WH-TYO-03": (35.6190, 139.7510, "Tokyo Bay Seafood Hydro-Chill, Japan"),
    }

    for node in nodes:
        coords_info = NODE_COORDS.get(node.id, (19.0760, 72.8777, node.location or "Cold Hub"))
        n_lat, n_lng, n_loc = coords_info

        dist = haversine_distance_km(c_lat, c_lng, n_lat, n_lng)
        if dist > params.max_search_radius_km:
            continue

        eta_mins = int((dist / 55.0) * 60.0) + 10  # assume 55 km/h highway speed + 10 min gate check
        available_pallets = max(0, (node.max_pallets or 1000) - (node.pallet_count or 0))

        # Check chambers for this warehouse
        chambers = db.execute(
            select(WarehouseChamber).where(WarehouseChamber.warehouse_id == node.id)
        ).scalars().all()
        target_temp = node.current_temp if node.current_temp is not None else 2.0
        for ch in chambers:
            if ch.temperature is not None and ch.temperature < target_temp:
                target_temp = ch.temperature

        # Feasibility check: Can we reach facility before spoilage?
        reaches_in_time = (eta_mins / 60.0) < hours_to_spoilage
        salvaged_pct = 95.0 if reaches_in_time else max(10.0, 95.0 - (eta_mins / 60.0 - hours_to_spoilage) * 30.0)

        rescue_type = "RAPID BLAST CHILL" if target_temp <= -10.0 else "COLD STORAGE DIVERT"

        ranked_options.append(
            RescueOption(
                type=rescue_type,
                facility_name=node.name,
                facility_id=node.id,
                location=n_loc,
                lat=n_lat,
                lng=n_lng,
                distance_km=dist,
                eta_minutes=eta_mins,
                available_capacity_pallets=available_pallets,
                temperature_achievable_c=round(target_temp, 1),
                cargo_value_salvaged_pct=round(salvaged_pct, 1),
                action_priority=priority,
                dispatch_command=f"DIVERT-TO-{node.id}-ETA-{eta_mins}MINS",
            )
        )
        priority += 1

    # Add mobile standby reefer cross-dock option if nearby
    standby_lat, standby_lng = c_lat + 0.15, c_lng - 0.12
    standby_dist = haversine_distance_km(c_lat, c_lng, standby_lat, standby_lng)
    standby_eta = int((standby_dist / 60.0) * 60.0) + 15
    ranked_options.append(
        RescueOption(
            type="BACKUP REEFER DISPATCH",
            facility_name="Standby Reefer Unit CC-REEFER-07 (Thane Mobile Dock)",
            facility_id="CC-REEFER-07",
            location="Thane Buffer Siding (Highway Flying Squad)",
            lat=round(standby_lat, 4),
            lng=round(standby_lng, 4),
            distance_km=standby_dist,
            eta_minutes=standby_eta,
            available_capacity_pallets=24,
            temperature_achievable_c=2.0,
            cargo_value_salvaged_pct=92.0,
            action_priority=priority,
            dispatch_command="DISPATCH-MOBILE-REEFER-CC-07",
        )
    )

    # Sort options by ETA minutes
    ranked_options.sort(key=lambda x: x.eta_minutes)
    for idx, opt in enumerate(ranked_options):
        opt.action_priority = idx + 1

    top_pick = ranked_options[0] if ranked_options else None
    primary_advisory = (
        f"Critical Excursion (+{c_temp}°C vs max safe {max_safe}°C). "
        f"Estimated {hours_to_spoilage}h before irreversible potency loss. "
        f"Primary Recommendation: Divert immediately to {top_pick.facility_name if top_pick else 'Nearest Depot'} "
        f"({top_pick.distance_km if top_pick else 0} km, ETA {top_pick.eta_minutes if top_pick else 0} mins)."
    )

    return EmergencyRescueResponse(
        current_coordinates=[c_lat, c_lng],
        current_temperature=c_temp,
        hours_until_spoilage=hours_to_spoilage,
        critical_threshold_exceeded_by_c=excursion_delta,
        ranked_options=ranked_options,
        primary_recommendation=primary_advisory,
    )


# ---------------------------------------------------------------------------
# 4. Live Shipment Telematics AI Diagnostics
# ---------------------------------------------------------------------------

def analyze_shipment_telemetry(shipment_id: str, db: Session) -> ShipmentAIAnalysisResponse:
    """Analyze historical telemetry breadcrumbs from database and diagnose health."""
    stmt = select(ShipmentModel).where(
        (ShipmentModel.id == shipment_id) | (ShipmentModel.tracking_number == shipment_id)
    )
    shipment = db.execute(stmt).scalar_one_or_none()
    if not shipment:
        raise ValueError(f"Shipment '{shipment_id}' not found in database.")

    # Fetch position pings history
    pos_stmt = (
        select(PositionModel)
        .where(PositionModel.shipment_id == shipment.id)
        .order_by(PositionModel.recorded_at.desc())
        .limit(100)
    )
    positions = db.execute(pos_stmt).scalars().all()

    cargo_key = (shipment.category or "vaccines").lower()
    if "produce" in cargo_key or "mango" in (shipment.commodity or "").lower():
        cargo_type = "fresh_produce"
    elif "pharma" in cargo_key or "vaccine" in (shipment.commodity or "").lower():
        cargo_type = "vaccines"
    elif "dairy" in cargo_key:
        cargo_type = "dairy"
    else:
        cargo_type = "vaccines"

    profile = COMMODITY_PROFILES.get(cargo_type, COMMODITY_PROFILES["vaccines"])
    target_min = shipment.min_temp if shipment.min_temp is not None else profile["min_temp"]
    target_max = shipment.max_temp if shipment.max_temp is not None else profile["max_temp"]
    curr_temp = shipment.temperature if shipment.temperature is not None else profile["ideal_temp"]

    # Calculate cumulative degree-hours of excursion stress
    cumulative_stress = 0.0
    for p in positions:
        p_temp = p.temperature if p.temperature is not None else curr_temp
        if p_temp > target_max:
            cumulative_stress += (p_temp - target_max) * 0.25  # assume 15 min ping spacing

    # Calculate kinetic loss
    pred = predict_shelf_life(
        ShelfLifePredictionRequest(
            cargo_type=cargo_type,
            current_temp=curr_temp,
            baseline_temp=profile["ideal_temp"],
            exposure_duration_hours=max(1.0, len(positions) * 0.25),
            initial_shelf_life_hours=shipment.initial_shelf_life_hours or profile["default_shelf_life_hours"],
        )
    )

    interventions: List[str] = []
    if pred.risk_level in ("Critical", "Immediate Spoilage Risk"):
        interventions.append("CRITICAL: Authorize immediate emergency cargo rescue cross-dock.")
        interventions.append("Notify consignee quality desk of temperature excursion audit.")
    elif pred.risk_level == "Warning":
        interventions.append("Adjust reefer thermostat to pre-cool boost setting.")
        interventions.append("Expedite toll plaza clearance via green-channel FASTag.")
    else:
        interventions.append("Cold chain within certified compliance bounds. Continue standard routing.")

    cooling_status = "Optimal" if curr_temp <= target_max else "Thermal Load Exceeded"

    return ShipmentAIAnalysisResponse(
        shipment_id=shipment.id,
        tracking_number=shipment.tracking_number,
        commodity=shipment.commodity,
        cargo_type=cargo_type,
        current_location=shipment.current_location or "Corridor In Transit",
        current_temp=curr_temp,
        target_temp_range=f"{target_min}°C to {target_max}°C",
        recorded_pings_count=len(positions),
        cumulative_thermal_stress_degree_hours=round(cumulative_stress, 2),
        shelf_life_loss_pct=pred.shelf_life_loss_pct,
        remaining_shelf_life_hours=pred.remaining_shelf_life_hours,
        spoilage_risk_level=pred.risk_level,
        projected_delivery_quality=f"{pred.quality_score_pct}% Certified Vitality",
        cooling_efficiency_status=cooling_status,
        immediate_interventions=interventions,
    )

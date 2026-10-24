"""Initial demonstration data seed script for ColdChain 360 Supabase database."""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure backend directory is in python search path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from sqlalchemy import select
from db.session import SessionLocal, engine
from services.auth import get_password_hash
from models import (
    User,
    Location,
    Truck,
    Driver,
    Shipment,
    Position,
    Event,
    Alert,
    WarehouseNode,
    WarehouseChamber,
    CropBatch,
    Assignment,
)


def seed_database():
    """Populate initial baseline demo records in Supabase if tables are unseeded."""
    db: Session = SessionLocal()
    try:
        print("[1/8] Checking existing users...")
        user_count = db.execute(select(User)).scalars().all()
        if not user_count:
            default_pwd = get_password_hash("ColdChain2026!")
            users_data = [
                User(
                    email="ops.lead@coldchain360.in",
                    hashed_password=default_pwd,
                    role="admin",
                    full_name="Vikramaditya Rao",
                    phone="+91 98200 11223",
                    organization="ColdChain 360 HQ",
                    location="Mumbai Command Center",
                    avatar="VR",
                    clearance_level="Chief Dispatcher · National Ops",
                    is_active=True,
                ),
                User(
                    email="truck.admin@coldchain360.in",
                    hashed_password=default_pwd,
                    role="truck_admin",
                    full_name="Vikramaditya Rao",
                    phone="+91 98200 11223",
                    organization="ColdChain 360 Highway Logistics",
                    location="Nagpur Multi-Modal Hub",
                    avatar="VR",
                    clearance_level="National Fleet Director · Reefer Division",
                    is_active=True,
                ),
                User(
                    email="kisan.rail@coldchain360.in",
                    hashed_password=default_pwd,
                    role="railway_admin",
                    full_name="Ashok Meena",
                    phone="+91 94140 22334",
                    organization="Western & Central DFC Logistics Division",
                    location="Bhusawal & JNPT Rail Terminal",
                    avatar="AM",
                    clearance_level="Chief Freight Controller · Kisan Rail Network",
                    is_active=True,
                ),
                User(
                    email="warehouse.lead@coldchain360.in",
                    hashed_password=default_pwd,
                    role="warehouse_admin",
                    full_name="Sunita Kulkarni",
                    phone="+91 98212 99881",
                    organization="Apex Mega Cold Chain Terminal",
                    location="Bhiwandi Cold Logistics Park",
                    avatar="SK",
                    clearance_level="General Manager · Cold Storage & CA Chambers",
                    is_active=True,
                ),
                User(
                    email="ramesh.deshmukh@agrocoop.in",
                    hashed_password=default_pwd,
                    role="farmer",
                    full_name="Ramesh Deshmukh",
                    phone="+91 98221 55678",
                    organization="Deshmukh Agro Producer Cooperative",
                    location="Ratnagiri, Maharashtra",
                    avatar="RD",
                    clearance_level="Verified Agro Producer · Class A1",
                    is_active=True,
                ),
                User(
                    email="rajesh.sharma@coldchain360.in",
                    hashed_password=default_pwd,
                    role="driver",
                    full_name="Rajesh Sharma",
                    phone="+91 98230 44102",
                    organization="ColdChain 360 Express",
                    location="NH-48 Corridor",
                    avatar="RS",
                    clearance_level="Master Heavy Hauler · Cold Reefer",
                    assigned_vehicle_id="CC-REEFER-01",
                    is_active=True,
                ),
                User(
                    email="supplychain@serumbiopharma.com",
                    hashed_password=default_pwd,
                    role="customer",
                    full_name="Serum BioPharma Consignee Desk",
                    phone="+91 20 6607 4000",
                    organization="Serum BioPharma Ltd.",
                    location="Pune Bio Park",
                    avatar="SB",
                    clearance_level="Enterprise Consignee (Pune Bio-Cluster)",
                    is_active=True,
                ),
            ]
            db.add_all(users_data)
            db.commit()
            print(f"-> Seeded {len(users_data)} users.")
        else:
            print(f"-> {len(user_count)} users already exist.")

        print("[2/8] Checking existing locations...")
        loc_count = db.execute(select(Location)).scalars().all()
        if not loc_count:
            locations = [
                Location(name="Ratnagiri Agro Orchard", address="Ratnagiri, Maharashtra, India", latitude=16.9902, longitude=73.3120, location_type="Origin Farm"),
                Location(name="Mumbai International Air Cargo (BOM)", address="Sahar, Andheri East, Mumbai, India", latitude=19.0896, longitude=72.8656, location_type="Airport"),
                Location(name="Panvel Multimodal Distribution Center", address="Panvel, Navi Mumbai, India", latitude=18.9894, longitude=73.1175, location_type="Hub"),
                Location(name="JNPT Port Container Terminal", address="Nhava Sheva, Navi Mumbai, India", latitude=18.9499, longitude=72.9511, location_type="Port"),
                Location(name="Bhiwandi Mega Cold Hub", address="Bhiwandi, Thane, Maharashtra, India", latitude=19.2967, longitude=73.0631, location_type="Warehouse"),
                Location(name="Basel BioTech Park", address="Basel, Switzerland", latitude=47.5596, longitude=7.5886, location_type="Origin Lab"),
                Location(name="Berlin Charité Clinic", address="Charitéplatz 1, Berlin, Germany", latitude=52.5251, longitude=13.3777, location_type="Hospital"),
            ]
            db.add_all(locations)
            db.commit()
            print(f"-> Seeded {len(locations)} locations.")
        else:
            print(f"-> {len(loc_count)} locations already exist.")

        print("[3/8] Checking existing trucks...")
        truck_count = db.execute(select(Truck)).scalars().all()
        if not truck_count:
            trucks = [
                Truck(
                    id="CC-REEFER-01",
                    plate_number="MH-12-AB-1234",
                    vehicle_type="Heavy Reefer 32T",
                    driver_name="Rajesh Sharma",
                    status="En Route",
                    reefer_health_score=94,
                    fuel_level=78,
                    current_cargo="Alphonso Premium Mangoes (CC-1048)",
                    compressor_pressure_psi=218.0,
                    refrigerant_level_pct=88,
                    current_location="NH-66 Khed Bypass (KM 142)",
                    latitude=17.712,
                    longitude=73.389,
                    current_temperature=9.8,
                    target_temperature=4.0,
                ),
                Truck(
                    id="CC-REEFER-02",
                    plate_number="MH-31-TR-4912",
                    vehicle_type="Tata Signa 4825.TK Heavy Carrier",
                    driver_name="Gurdeep Singh",
                    status="En Route",
                    reefer_health_score=97,
                    fuel_level=85,
                    current_cargo="Rabies Vaccine Consignment (CC-8092)",
                    compressor_pressure_psi=225.0,
                    refrigerant_level_pct=96,
                    current_location="Nashik Agro Terminal",
                    latitude=19.9975,
                    longitude=73.7898,
                    current_temperature=4.2,
                    target_temperature=4.0,
                ),
                Truck(
                    id="CC-REEFER-03",
                    plate_number="MH-14-GH-7788",
                    vehicle_type="BharatBenz 3528R Sub-Zero Reefer",
                    driver_name="Suresh Patil",
                    status="Docking",
                    reefer_health_score=98,
                    fuel_level=92,
                    current_cargo="Frozen Buffalo Butter",
                    compressor_pressure_psi=210.0,
                    refrigerant_level_pct=98,
                    current_location="Pune Cold Hub Siding",
                    latitude=18.5204,
                    longitude=73.8567,
                    current_temperature=-18.5,
                    target_temperature=-20.0,
                ),
                Truck(
                    id="CC-REEFER-04",
                    plate_number="MH-46-AR-2201",
                    vehicle_type="Mahindra Blazo X Pharma Reefer",
                    driver_name="Mohan Kumar",
                    status="En Route",
                    reefer_health_score=95,
                    fuel_level=70,
                    current_cargo="Bhagwa Pomegranate Export",
                    compressor_pressure_psi=220.0,
                    refrigerant_level_pct=92,
                    current_location="Mumbai Nhava Sheva Buffer",
                    latitude=18.9500,
                    longitude=72.9500,
                    current_temperature=5.4,
                    target_temperature=5.0,
                ),
                Truck(
                    id="CC-REEFER-05",
                    plate_number="MH-04-AZ-4419",
                    vehicle_type="Eicher Pro 6028 Dual-Temp",
                    driver_name="Amit Verma",
                    status="Standby",
                    reefer_health_score=90,
                    fuel_level=95,
                    current_cargo="Empty - Pre-cooled to 3°C",
                    compressor_pressure_psi=205.0,
                    refrigerant_level_pct=95,
                    current_location="Nagpur Central Maintenance Base",
                    latitude=21.1458,
                    longitude=79.0882,
                    current_temperature=3.0,
                    target_temperature=3.0,
                ),
            ]
            db.add_all(trucks)
            db.commit()
            print(f"-> Seeded {len(trucks)} trucks.")
        else:
            print(f"-> {len(truck_count)} trucks already exist.")

        print("[4/8] Checking existing drivers...")
        drv_count = db.execute(select(Driver)).scalars().all()
        if not drv_count:
            drivers = [
                Driver(name="Rajesh Sharma", license_number="MH-12-201500981", phone="+91 98230 44102", email="rajesh.sharma@coldchain360.in", status="On Trip", assigned_vehicle_id="CC-REEFER-01", experience_years=8.5, rating=4.9, total_trips=214),
                Driver(name="Gurdeep Singh", license_number="PB-08-201200452", phone="+91 98110 55219", email="gurdeep.singh@coldchain360.in", status="On Trip", assigned_vehicle_id="CC-REEFER-02", experience_years=11.0, rating=4.8, total_trips=340),
                Driver(name="Suresh Patil", license_number="MH-14-201800119", phone="+91 94220 88314", email="suresh.patil@coldchain360.in", status="Available", assigned_vehicle_id="CC-REEFER-03", experience_years=6.0, rating=4.7, total_trips=160),
                Driver(name="Mohan Kumar", license_number="KA-05-201600783", phone="+91 97330 19283", email="mohan.kumar@coldchain360.in", status="On Trip", assigned_vehicle_id="CC-REEFER-04", experience_years=7.5, rating=4.9, total_trips=195),
                Driver(name="Amit Verma", license_number="MH-31-201900228", phone="+91 94221 80107", email="amit.verma@coldchain360.in", status="Available", assigned_vehicle_id="CC-REEFER-05", experience_years=4.5, rating=4.6, total_trips=98),
            ]
            db.add_all(drivers)
            db.commit()
            print(f"-> Seeded {len(drivers)} drivers.")
        else:
            print(f"-> {len(drv_count)} drivers already exist.")

        print("[5/8] Checking existing warehouse nodes and chambers...")
        node_count = db.execute(select(WarehouseNode)).scalars().all()
        if not node_count:
            nodes = [
                WarehouseNode(id="WH-BOM-01", name="Panvel Western Cold Hub Alpha", location="Navi Mumbai, India", zone="Zone 1 (Produce & Fruits: +2°C to +6°C)", current_temp=3.8, target_temp=4.0, capacity_used_percentage=78, pallet_count=1240, max_pallets=1600, risk_status="Optimal", expiring_lots_count=3),
                WarehouseNode(id="WH-MAH-02", name="Mahad Emergency Agro Preservation Depot", location="Mahad Industrial Zone, Maharashtra", zone="Rapid Blast Chill (Zone A: +0°C to +4°C)", current_temp=2.1, target_temp=2.0, capacity_used_percentage=42, pallet_count=340, max_pallets=800, risk_status="Optimal", expiring_lots_count=0),
                WarehouseNode(id="WH-FRA-01", name="Frankfurt Deep Cryo Bio-Logistics Hub", location="Frankfurt Airport CargoCity South, Germany", zone="Ultra Low Cryo (-80°C)", current_temp=-78.6, target_temp=-80.0, capacity_used_percentage=89, pallet_count=445, max_pallets=500, risk_status="Optimal", expiring_lots_count=1),
                WarehouseNode(id="WH-TYO-03", name="Tokyo Bay Seafood Hydro-Chill Warehouse", location="Shinagawa Port, Tokyo, Japan", zone="Super-Chilled Brine (-1.5°C)", current_temp=-1.2, target_temp=-1.5, capacity_used_percentage=92, pallet_count=2200, max_pallets=2400, risk_status="Caution", expiring_lots_count=8),
            ]
            db.add_all(nodes)
            db.commit()

            chambers = [
                WarehouseChamber(chamber_id="CH-01", warehouse_id="WH-BOM-01", name="Chamber 1 · Deep Sub-Zero Cryo", chamber_type="Deep Freeze", temperature=-24.8, target_temp=-25.0, humidity_rh=82.0, target_humidity_rh=80.0, pallet_capacity=1200, occupied_pallets=1080, refrigerant_status="Optimal · Freon R404A", ammonia_ppm=0.2, status="Active"),
                WarehouseChamber(chamber_id="CH-02", warehouse_id="WH-BOM-01", name="Chamber 2 · Pharma & Biologics Chiller", chamber_type="Chilled Cold Room", temperature=4.1, target_temp=4.0, humidity_rh=65.0, target_humidity_rh=65.0, pallet_capacity=800, occupied_pallets=742, refrigerant_status="Normal · Ammonia NH3", ammonia_ppm=0.8, status="Active"),
                WarehouseChamber(chamber_id="CH-03", warehouse_id="WH-BOM-01", name="Chamber 3 · Controlled Atmosphere (CA) Produce", chamber_type="Controlled Atmosphere (CA)", temperature=0.8, target_temp=1.0, humidity_rh=94.5, target_humidity_rh=95.0, gas_o2_percent=1.4, gas_co2_percent=1.1, pallet_capacity=1500, occupied_pallets=1390, refrigerant_status="Normal · Ammonia NH3", ammonia_ppm=0.5, status="Active"),
                WarehouseChamber(chamber_id="CH-04", warehouse_id="WH-MAH-02", name="Chamber 4 · Rapid Blast Freezing Tunnel", chamber_type="Blast Freezer Tunnel", temperature=-38.2, target_temp=-40.0, humidity_rh=80.0, target_humidity_rh=80.0, pallet_capacity=250, occupied_pallets=160, refrigerant_status="Optimal · Freon R404A", ammonia_ppm=0.1, status="Pre-Cooling"),
            ]
            db.add_all(chambers)
            db.commit()
            print(f"-> Seeded {len(nodes)} warehouses and {len(chambers)} chambers.")
        else:
            print(f"-> {len(node_count)} warehouses already exist.")

        print("[6/8] Checking existing shipments and alerts...")
        ship_count = db.execute(select(Shipment)).scalars().all()
        if not ship_count:
            shipments = [
                Shipment(
                    id="CC-1048",
                    tracking_number="CC360-IND-8849-MH",
                    commodity="Alphonso Premium Mangoes (Export Grade)",
                    category="Fresh Produce",
                    origin="Ratnagiri Agro Orchard, Maharashtra",
                    destination="Mumbai International Air Cargo (BOM)",
                    current_location="NH-66 Khed Bypass (Lat: 17.712, Lon: 73.389)",
                    carrier="ColdTrans Logistics Fleet 4",
                    mode="Road",
                    temperature=9.8,
                    min_temp=4.0,
                    max_temp=7.0,
                    humidity=89,
                    battery_level=94,
                    reefer_status="Compressor Warning",
                    door_status="Sealed & Locked",
                    gps_signal="Strong (5G/LEO)",
                    risk_score=84,
                    risk_level="Critical",
                    remaining_shelf_life_hours=19.5,
                    initial_shelf_life_hours=72.0,
                    eta="Today · 19:45 IST",
                    original_eta="Today · 17:15 IST",
                    shock_g=0.18,
                    light_lux=0,
                    farmer_producer="Deshmukh Agro Farms Cooperative",
                    economic_value="$48,500",
                    co2_saved_kg=420,
                    status="Critical Alert",
                    waypoints=[
                        {"name": "Ratnagiri Cold Storage Facility", "type": "Farm", "completed": True, "timestamp": "06:30 IST"},
                        {"name": "Khed Transit Corridor", "type": "Truck", "completed": True, "current": True, "timestamp": "14:15 IST"},
                        {"name": "Panvel Multimodal Distribution Center", "type": "Hub", "completed": False},
                        {"name": "Mumbai Airport Cold Terminal 2", "type": "Airport", "completed": False},
                        {"name": "Global Importers Terminal Heathrow (LHR)", "type": "Buyer", "completed": False},
                    ],
                    temperature_history=[
                        {"time": "08:00", "temp": 4.8, "ambientTemp": 28.5, "safeMin": 4.0, "safeMax": 7.0},
                        {"time": "10:00", "temp": 5.1, "ambientTemp": 32.1, "safeMin": 4.0, "safeMax": 7.0},
                        {"time": "12:00", "temp": 6.2, "ambientTemp": 35.4, "safeMin": 4.0, "safeMax": 7.0},
                        {"time": "13:30", "temp": 7.8, "ambientTemp": 37.0, "safeMin": 4.0, "safeMax": 7.0},
                        {"time": "14:30", "temp": 9.8, "ambientTemp": 38.2, "safeMin": 4.0, "safeMax": 7.0},
                    ],
                ),
                Shipment(
                    id="CC-2210",
                    tracking_number="CC360-EUR-4412-BIO",
                    commodity="mRNA Oncology Vaccines (Pediatric)",
                    category="Biologics",
                    origin="BioTech Park Basel, Switzerland",
                    destination="Charité University Hospital, Berlin",
                    current_location="Frankfurt Intermodal Rail Yard",
                    carrier="Swiss-German Rail Cargo CryoLink",
                    mode="Rail",
                    temperature=-71.4,
                    min_temp=-80.0,
                    max_temp=-65.0,
                    humidity=12,
                    battery_level=98,
                    reefer_status="Active & Optimal",
                    door_status="Sealed & Locked",
                    gps_signal="Strong (5G/LEO)",
                    risk_score=6,
                    risk_level="Nominal",
                    remaining_shelf_life_hours=540.0,
                    initial_shelf_life_hours=720.0,
                    eta="Tomorrow · 06:00 CET",
                    original_eta="Tomorrow · 06:00 CET",
                    shock_g=0.05,
                    light_lux=0,
                    farmer_producer="Novavita Bio Therapeutics AG",
                    economic_value="$340,000",
                    co2_saved_kg=1280,
                    status="In Transit",
                    waypoints=[
                        {"name": "Basel Bio-Campus Vault 1", "type": "Hub", "completed": True, "timestamp": "Yesterday 22:00"},
                        {"name": "Mannheim Central Freight Track", "type": "Rail", "completed": True, "timestamp": "04:15"},
                        {"name": "Frankfurt High-Speed Rail Siding", "type": "Rail", "completed": True, "current": True, "timestamp": "12:00"},
                        {"name": "Berlin South Logistics Terminal", "type": "Warehouse", "completed": False},
                        {"name": "Charité Clinic Central Pharmacy", "type": "Buyer", "completed": False},
                    ],
                    temperature_history=[
                        {"time": "02:00", "temp": -72.0, "ambientTemp": 14.0, "safeMin": -80.0, "safeMax": -65.0},
                        {"time": "05:00", "temp": -71.8, "ambientTemp": 12.5, "safeMin": -80.0, "safeMax": -65.0},
                        {"time": "08:00", "temp": -71.5, "ambientTemp": 18.0, "safeMin": -80.0, "safeMax": -65.0},
                        {"time": "11:00", "temp": -71.4, "ambientTemp": 21.2, "safeMin": -80.0, "safeMax": -65.0},
                        {"time": "14:00", "temp": -71.4, "ambientTemp": 22.0, "safeMin": -80.0, "safeMax": -65.0},
                    ],
                ),
                Shipment(
                    id="CC-3091",
                    tracking_number="CC360-NOR-9011-SEA",
                    commodity="Wild Atlantic Salmon (Sashimi Grade)",
                    category="Seafood",
                    origin="Tromsø Aquaculture Harbor, Norway",
                    destination="Tsukiji Direct Global Market, Tokyo",
                    current_location="Helsinki Vantaa Airport Cargo Bay 9",
                    carrier="Nordic Air Freight Cargo 802",
                    mode="Air",
                    temperature=0.4,
                    min_temp=-1.0,
                    max_temp=2.0,
                    humidity=94,
                    battery_level=87,
                    reefer_status="Active & Optimal",
                    door_status="Sealed & Locked",
                    gps_signal="Strong (5G/LEO)",
                    risk_score=18,
                    risk_level="Guarded",
                    remaining_shelf_life_hours=84.0,
                    initial_shelf_life_hours=120.0,
                    eta="Tomorrow · 11:30 JST",
                    original_eta="Tomorrow · 11:30 JST",
                    shock_g=0.12,
                    light_lux=0,
                    farmer_producer="Nordic Blue Fjord Marine Ltd",
                    economic_value="$92,000",
                    co2_saved_kg=850,
                    status="In Transit",
                    waypoints=[
                        {"name": "Tromsø Deep Sea Processing Point", "type": "Farm", "completed": True, "timestamp": "Day -1"},
                        {"name": "Narvik Cold Express Transit", "type": "Truck", "completed": True},
                        {"name": "Helsinki Vantaa Air Hub", "type": "Airport", "completed": True, "current": True},
                        {"name": "Tokyo Narita Bonded Cargo", "type": "Airport", "completed": False},
                        {"name": "Tokyo Tsukiji Fish Terminal", "type": "Buyer", "completed": False},
                    ],
                    temperature_history=[
                        {"time": "00:00", "temp": 0.2, "ambientTemp": -2.0, "safeMin": -1.0, "safeMax": 2.0},
                        {"time": "04:00", "temp": 0.3, "ambientTemp": 3.0, "safeMin": -1.0, "safeMax": 2.0},
                        {"time": "08:00", "temp": 0.5, "ambientTemp": 11.0, "safeMin": -1.0, "safeMax": 2.0},
                        {"time": "12:00", "temp": 0.4, "ambientTemp": 14.5, "safeMin": -1.0, "safeMax": 2.0},
                    ],
                ),
                Shipment(
                    id="CC-4015",
                    tracking_number="CC360-USA-7712-DAI",
                    commodity="Artisanal Organic Cultured Butter & Cheeses",
                    category="Dairy",
                    origin="Sonoma Valley Dairy Co-op, California",
                    destination="Whole Foods Regional Fulfillment, Austin TX",
                    current_location="I-10 Eastbound, Las Cruces NM",
                    carrier="TransContinental Coldways Reefer 112",
                    mode="Road",
                    temperature=3.6,
                    min_temp=1.0,
                    max_temp=4.5,
                    humidity=78,
                    battery_level=91,
                    reefer_status="Active & Optimal",
                    door_status="Sealed & Locked",
                    gps_signal="Strong (5G/LEO)",
                    risk_score=24,
                    risk_level="Guarded",
                    remaining_shelf_life_hours=280.0,
                    initial_shelf_life_hours=360.0,
                    eta="Oct 28 · 08:00 CDT",
                    original_eta="Oct 28 · 08:00 CDT",
                    shock_g=0.08,
                    light_lux=0,
                    farmer_producer="Sonoma Valley Artisan Organic Dairies",
                    economic_value="$64,000",
                    co2_saved_kg=610,
                    status="In Transit",
                    waypoints=[
                        {"name": "Sonoma Processing Dairy", "type": "Farm", "completed": True},
                        {"name": "Bakersfield Cross-Dock Station", "type": "Hub", "completed": True},
                        {"name": "Las Cruces Route Checkpoint", "type": "Truck", "completed": True, "current": True},
                        {"name": "Austin Central Distribution Center", "type": "Warehouse", "completed": False},
                    ],
                    temperature_history=[
                        {"time": "06:00", "temp": 3.2, "ambientTemp": 24.0, "safeMin": 1.0, "safeMax": 4.5},
                        {"time": "09:00", "temp": 3.4, "ambientTemp": 28.0, "safeMin": 1.0, "safeMax": 4.5},
                        {"time": "12:00", "temp": 3.6, "ambientTemp": 34.0, "safeMin": 1.0, "safeMax": 4.5},
                    ],
                ),
                Shipment(
                    id="CC-8092",
                    tracking_number="CC360-IND-8092-PH",
                    commodity="Rabies Vaccine Consignment (Cold Box 4)",
                    category="Pharma",
                    origin="Serum Institute of India, Hadapsar, Pune",
                    destination="KEM Hospital Blood Bank & Pharmacy, Mumbai",
                    current_location="Mumbai-Pune Expressway (KM 64)",
                    carrier="ColdChain 360 Express Reefer 01",
                    mode="Road",
                    temperature=3.8,
                    min_temp=2.0,
                    max_temp=8.0,
                    humidity=65,
                    battery_level=96,
                    reefer_status="Active & Optimal",
                    door_status="Sealed & Locked",
                    gps_signal="Strong (5G/LEO)",
                    risk_score=12,
                    risk_level="Nominal",
                    remaining_shelf_life_hours=720.0,
                    initial_shelf_life_hours=720.0,
                    eta="Today · 16:30 IST",
                    original_eta="Today · 16:30 IST",
                    shock_g=0.04,
                    light_lux=0,
                    farmer_producer="Serum BioPharma Ltd",
                    economic_value="$180,000",
                    co2_saved_kg=310,
                    status="In Transit",
                    truck_id="CC-REEFER-01",
                ),
            ]
            db.add_all(shipments)
            db.commit()

            alert = Alert(
                id="ALT-8849-01",
                shipment_id="CC-1048",
                truck_id="CC-REEFER-01",
                alert_type="Temperature Excursion",
                severity="critical",
                title="Dynamic Shelf-Life Exhaustion Imminent (+2.8°C Above Max Threshold)",
                description="Thermal rise detected over past 90 mins due to primary secondary coil micro-leakage. Model predicts total enzymatic softening & mold onset in 19.5 hours, 3.5 hours before cargo reaches bonded air freight customs.",
                predicted_excursion_time="16:00 IST (+1.5 hrs)",
                predicted_loss_usd="$48,500 (100% consignment loss)",
                recommended_actions=[
                    {
                        "id": "REC-01",
                        "title": "Emergency Divert to Mahad Agro Cold Hub (Recommended)",
                        "description": "Divert vehicle 18km to Mahad Cold Chain Hub. Dock bay 4 is pre-reserved at 3.8°C. Cargo can be inspected and cross-docked into backup reefer #RF-904.",
                        "shelfLifePreserved": "68.5 hours (+250%)",
                        "costDelta": "+$320 logistics fee",
                        "etaChange": "+2 hrs to airport buffer",
                        "co2Delta": "-14kg CO2e",
                        "confidence": 96.4,
                        "recommended": True,
                    },
                    {
                        "id": "REC-02",
                        "title": "Switch to On-demand Reefer Rendezvous",
                        "description": "Deploy idle CryoReefer #CR-201 from Chiplun depot for mid-highway trailer transfer at Poladpur rest station.",
                        "shelfLifePreserved": "54 hours",
                        "costDelta": "+$750 emergency haul",
                        "etaChange": "+45 mins",
                        "co2Delta": "+32kg CO2e",
                        "confidence": 88.1,
                        "recommended": False,
                    },
                ],
                is_acknowledged=False,
                is_resolved=False,
            )
            db.add(alert)
            db.commit()
            print(f"-> Seeded {len(shipments)} shipments and 1 critical alert.")
        else:
            print(f"-> {len(ship_count)} shipments already exist.")

        print("[7/8] Checking existing crop batches...")
        batch_count = db.execute(select(CropBatch)).scalars().all()
        if not batch_count:
            batches = [
                CropBatch(
                    id="LOT-AGRO-701",
                    crop="Alphonso Mango",
                    variety="GI Tagged Ratnagiri",
                    farmer_name="Ramesh Deshmukh",
                    farm_location="Ratnagiri, Maharashtra",
                    harvest_date="2026-10-21",
                    quantity_tons=14.5,
                    initial_temp=28.5,
                    current_temp=11.2,
                    target_temp=10.0,
                    temp_safe=True,
                    humidity=88.0,
                    shelf_life_days_total=21,
                    shelf_life_remaining_days=16,
                    grade="A",
                    quality_score=94,
                    cargo_health_score=94,
                    status="In-Transit",
                    allocated_hub="Bhiwandi Mega Cold Hub",
                    assigned_vehicle="CC-REEFER-01",
                    mandi_rate_per_kg=195.0,
                    escrow_secured_amount=2827500.0,
                    payout_status="Escrow Secured",
                    payout_amount="₹28,27,500 ($34,100)",
                    subsidy_eligible="PMKSY Cold Chain Grant (35%)",
                    sensor_verification_score=99,
                    qr_payload="CC360://CROP/LOT-AGRO-701/RATNAGIRI/MANGO-A/20261021",
                    eta="Today · 19:45 IST",
                ),
                CropBatch(
                    id="LOT-AGRO-702",
                    crop="Pomegranate",
                    variety="Bhagwa Export Grade",
                    farmer_name="Sanjay Patil",
                    farm_location="Solapur, Maharashtra",
                    harvest_date="2026-10-20",
                    quantity_tons=22.0,
                    initial_temp=26.0,
                    current_temp=5.4,
                    target_temp=5.0,
                    temp_safe=True,
                    humidity=92.0,
                    shelf_life_days_total=60,
                    shelf_life_remaining_days=52,
                    grade="A",
                    quality_score=97,
                    cargo_health_score=97,
                    status="In-Transit",
                    allocated_hub="JNPT Port Container Terminal",
                    assigned_vehicle="CC-REEFER-04",
                    mandi_rate_per_kg=140.0,
                    escrow_secured_amount=3080000.0,
                    payout_status="Escrow Secured",
                    payout_amount="₹30,80,000 ($37,200)",
                    subsidy_eligible="APEDA Cold Logistics Scheme",
                    sensor_verification_score=100,
                    qr_payload="CC360://CROP/LOT-AGRO-702/SOLAPUR/BHAGWA-A/20261020",
                    eta="Tomorrow · 10:00 GST",
                ),
                CropBatch(
                    id="LOT-AGRO-703",
                    crop="Table Grapes",
                    variety="Thomson Seedless",
                    farmer_name="Kailash Shinde",
                    farm_location="Nashik, Maharashtra",
                    harvest_date="2026-10-19",
                    quantity_tons=18.2,
                    initial_temp=24.0,
                    current_temp=1.8,
                    target_temp=1.0,
                    temp_safe=True,
                    humidity=94.0,
                    shelf_life_days_total=45,
                    shelf_life_remaining_days=38,
                    grade="A",
                    quality_score=92,
                    cargo_health_score=92,
                    status="Stored",
                    allocated_hub="Nashik Pre-Cooling Center",
                    assigned_vehicle="CC-REEFER-08",
                    mandi_rate_per_kg=110.0,
                    escrow_secured_amount=2002000.0,
                    payout_status="Processing",
                    payout_amount="₹20,02,000 ($24,100)",
                    subsidy_eligible="MIDH Packhouse Capital Grant",
                    sensor_verification_score=98,
                    qr_payload="CC360://CROP/LOT-AGRO-703/NASHIK/GRAPES-A/20261019",
                    eta="Delivered to Siding",
                ),
                CropBatch(
                    id="LOT-AGRO-704",
                    crop="Strawberries",
                    variety="Winter Dawn Sweet",
                    farmer_name="Anand More",
                    farm_location="Mahabaleshwar, Maharashtra",
                    harvest_date="2026-10-21",
                    quantity_tons=6.8,
                    initial_temp=22.0,
                    current_temp=3.2,
                    target_temp=2.0,
                    temp_safe=True,
                    humidity=95.0,
                    shelf_life_days_total=10,
                    shelf_life_remaining_days=7,
                    grade="B",
                    quality_score=86,
                    cargo_health_score=86,
                    status="Pre-Cooling",
                    allocated_hub="Pune Bio & Perishable Air Cargo",
                    mandi_rate_per_kg=280.0,
                    escrow_secured_amount=1904000.0,
                    payout_status="Escrow Secured",
                    payout_amount="₹19,04,000 ($23,000)",
                    subsidy_eligible="PM Formalisation of Micro FME",
                    sensor_verification_score=99,
                    qr_payload="CC360://CROP/LOT-AGRO-704/MAHABALESHWAR/STRAWBERRY/20261021",
                    eta="Today · 21:00 IST",
                ),
            ]
            db.add_all(batches)
            db.commit()
            print(f"-> Seeded {len(batches)} crop batches.")
        else:
            print(f"-> {len(batch_count)} crop batches already exist.")

        print("[8/8] Checking existing assignments...")
        assign_count = db.execute(select(Assignment)).scalars().all()
        if not assign_count:
            assignment = Assignment(
                shipment_id="CC-1048",
                truck_id="CC-REEFER-01",
                driver_id=1,
                status="Active",
                notes="Assigned for emergency high-priority reefer haul",
            )
            db.add(assignment)
            db.commit()
            print("-> Seeded 1 initial dispatch assignment.")
        else:
            print(f"-> {len(assign_count)} assignments already exist.")

        print("\n=== Data Seeding Completed Successfully! ===")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

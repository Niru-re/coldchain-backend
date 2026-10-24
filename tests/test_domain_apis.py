"""Integration tests for ColdChain 360 domain endpoints:
Shipments, Fleet, Alerts, Warehouses, Portals, Analytics, and User Management.
"""

import pytest
from fastapi import status


def get_auth_headers(client, email="dispatcher@coldchain360.in", password="Password123!"):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestShipmentsEndpoints:
    """Test shipment CRUD, filtering, and telematics."""

    def test_list_shipments_empty(self, client):
        response = client.get("/api/v1/shipments")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_create_and_get_shipment(self, client):
        headers = get_auth_headers(client, "creator@coldchain360.in")
        payload = {
            "id": "CC-TEST-01",
            "trackingNumber": "CC360-TEST-001",
            "commodity": "Alphonso Mangoes",
            "category": "Fresh Produce",
            "origin": "Ratnagiri Orchard",
            "destination": "Mumbai Port",
            "currentLocation": "Ratnagiri Hub",
            "carrier": "ColdChain Fleet",
            "mode": "Road",
            "status": "In Transit",
            "temperature": 5.2,
            "minTemp": 2.0,
            "maxTemp": 8.0,
            "humidity": 85.0,
            "batteryLevel": 95,
            "reeferStatus": "Active & Optimal",
            "doorStatus": "Sealed & Locked",
            "gpsSignal": "Strong",
            "riskScore": 12,
            "riskLevel": "Nominal",
            "remainingShelfLifeHours": 96.0,
            "initialShelfLifeHours": 120.0,
            "eta": "Tomorrow · 10:00 IST",
            "originalEta": "Tomorrow · 10:00 IST",
            "economicValue": "$35,000",
            "co2SavedKg": 420,
            "waypoints": [
                {"name": "Ratnagiri Hub", "type": "Farm", "completed": True}
            ],
            "temperatureHistory": [
                {"time": "08:00", "temp": 5.0, "ambientTemp": 28.0, "safeMin": 2.0, "safeMax": 8.0}
            ],
        }
        res_create = client.post("/api/v1/shipments", json=payload, headers=headers)
        assert res_create.status_code == status.HTTP_201_CREATED
        created = res_create.json()
        assert created["id"] == "CC-TEST-01"
        assert created["commodity"] == "Alphonso Mangoes"

        # Fetch by ID
        res_get = client.get("/api/v1/shipments/CC-TEST-01")
        assert res_get.status_code == status.HTTP_200_OK
        fetched = res_get.json()
        assert fetched["id"] == "CC-TEST-01"
        assert fetched["temperature"] == 5.2

    def test_update_shipment(self, client):
        headers = get_auth_headers(client, "updater@coldchain360.in")
        # Create first
        payload = {
            "id": "CC-UPDATE-01",
            "trackingNumber": "CC360-TEST-UPD",
            "commodity": "Vaccines",
            "category": "Pharma",
            "origin": "Pune BioPark",
            "destination": "Mumbai Hospital",
            "currentLocation": "Expressway KM 20",
            "carrier": "BioExpress",
            "mode": "Road",
            "status": "In Transit",
            "temperature": 4.0,
            "minTemp": 2.0,
            "maxTemp": 8.0,
            "remainingShelfLifeHours": 480.0,
            "initialShelfLifeHours": 720.0,
            "eta": "Today · 18:00 IST",
            "originalEta": "Today · 18:00 IST",
        }
        res_c = client.post("/api/v1/shipments", json=payload, headers=headers)
        assert res_c.status_code == status.HTTP_201_CREATED

        # Update status and temperature
        res_update = client.patch(
            "/api/v1/shipments/CC-UPDATE-01",
            json={"temperature": 4.8, "status": "Delivered"},
            headers=headers,
        )
        assert res_update.status_code == status.HTTP_200_OK
        updated = res_update.json()
        assert updated["temperature"] == 4.8
        assert updated["status"] == "Delivered"

    def test_telematics_ping(self, client):
        headers = get_auth_headers(client, "pinger@coldchain360.in")
        # Create shipment
        payload = {
            "id": "CC-PING-01",
            "trackingNumber": "CC360-TEST-PNG",
            "commodity": "Strawberries",
            "category": "Fresh Produce",
            "origin": "Mahabaleshwar",
            "destination": "Pune",
            "currentLocation": "Wai Ghat",
            "carrier": "Fleet 1",
            "mode": "Road",
            "status": "In Transit",
            "temperature": 3.0,
            "minTemp": 1.0,
            "maxTemp": 5.0,
            "remainingShelfLifeHours": 48.0,
            "initialShelfLifeHours": 72.0,
            "eta": "Today · 14:00 IST",
            "originalEta": "Today · 14:00 IST",
        }
        client.post("/api/v1/shipments", json=payload, headers=headers)

        # Record telematics ping
        ping = {
            "shipment_id": "CC-PING-01",
            "latitude": 17.9450,
            "longitude": 73.8180,
            "speed": 62.0,
            "ambient_temp": 28.5,
            "cargo_temp": 3.2,
        }
        res_ping = client.post("/api/v1/shipments/telematics/ping", json=ping)
        assert res_ping.status_code == status.HTTP_201_CREATED
        data = res_ping.json()
        assert data["status"] == "recorded"


class TestFleetEndpoints:
    """Test trucks, drivers, and dispatch assignments."""

    def test_truck_crud(self, client):
        truck_payload = {
            "id": "CC-TRK-TEST",
            "plate_number": "MH-12-QQ-9999",
            "vehicle_type": "Heavy Reefer 32T",
            "driver_name": "Test Driver",
            "status": "Standby",
            "reefer_health_score": 96,
            "fuel_level": 90,
            "compressor_pressure_psi": 210.0,
            "refrigerant_level_pct": 95,
        }
        res_create = client.post("/api/v1/fleet/trucks", json=truck_payload)
        assert res_create.status_code == status.HTTP_201_CREATED
        created = res_create.json()
        assert created["id"] == "CC-TRK-TEST"

        res_list = client.get("/api/v1/fleet/trucks")
        assert res_list.status_code == status.HTTP_200_OK
        trucks = res_list.json()
        assert any(t["id"] == "CC-TRK-TEST" for t in trucks)

    def test_driver_crud(self, client):
        driver_payload = {
            "name": "Arun Kumar",
            "license_number": "MH-12-TEST-88",
            "phone": "+91 99999 88888",
            "status": "Available",
            "experience_years": 5.0,
            "rating": 4.9,
        }
        res_create = client.post("/api/v1/fleet/drivers", json=driver_payload)
        assert res_create.status_code == status.HTTP_201_CREATED
        created = res_create.json()
        assert created["name"] == "Arun Kumar"

        res_list = client.get("/api/v1/fleet/drivers")
        assert res_list.status_code == status.HTTP_200_OK
        drivers = res_list.json()
        assert any(d["name"] == "Arun Kumar" for d in drivers)


class TestAlertsEndpoints:
    """Test alert creation, listing, acknowledgment, and resolution."""

    def test_alert_lifecycle(self, client):
        alert_payload = {
            "id": "ALT-TEST-001",
            "alert_type": "Temperature Excursion",
            "severity": "critical",
            "title": "Thermal Deviation on Refrigerator Coil",
            "description": "Temperature increased by 3.2°C above max target threshold.",
            "recommended_actions": [
                {"id": "ACT-1", "title": "Check compressor relay"}
            ],
        }
        res_create = client.post("/api/v1/alerts", json=alert_payload)
        assert res_create.status_code == status.HTTP_201_CREATED
        created = res_create.json()
        assert created["id"] == "ALT-TEST-001"
        assert not created["is_acknowledged"]
        assert not created["is_resolved"]

        # Acknowledge
        res_ack = client.post(
            "/api/v1/alerts/ALT-TEST-001/acknowledge",
            json={"acknowledged_by": "Ops Manager"},
        )
        assert res_ack.status_code == status.HTTP_200_OK
        assert res_ack.json()["is_acknowledged"] is True

        # Resolve
        res_res = client.post(
            "/api/v1/alerts/ALT-TEST-001/resolve",
            json={"resolution_notes": "Defrost cycle completed, temperature back to 4°C."},
        )
        assert res_res.status_code == status.HTTP_200_OK
        assert res_res.json()["is_resolved"] is True


class TestWarehousesEndpoints:
    """Test warehouse nodes and cold chambers."""

    def test_warehouse_node_and_chamber(self, client):
        node_payload = {
            "id": "WH-TEST-01",
            "name": "Nashik Agro Cold Hub",
            "location": "Nashik, Maharashtra",
            "zone": "Zone 1",
            "current_temp": 3.8,
            "target_temp": 4.0,
            "capacity_used_percentage": 65,
            "pallet_count": 650,
            "max_pallets": 1000,
            "risk_status": "Optimal",
            "expiring_lots_count": 0,
        }
        res_node = client.post("/api/v1/warehouses/nodes", json=node_payload)
        assert res_node.status_code == status.HTTP_201_CREATED

        chamber_payload = {
            "chamber_id": "CH-TEST-01",
            "warehouse_id": "WH-TEST-01",
            "name": "Chamber A1",
            "chamber_type": "Chilled Cold Room",
            "temperature": 3.5,
            "target_temp": 4.0,
            "humidity_rh": 90.0,
            "target_humidity_rh": 90.0,
            "pallet_capacity": 500,
            "occupied_pallets": 320,
            "refrigerant_status": "Optimal",
            "ammonia_ppm": 0.1,
            "status": "Active",
        }
        res_chamber = client.post("/api/v1/warehouses/chambers", json=chamber_payload)
        assert res_chamber.status_code == status.HTTP_201_CREATED


class TestPortalsEndpoints:
    """Test farmer crop batches, mandi rates, railway trains, and inspections."""

    def test_farmer_batch_crud(self, client):
        batch_payload = {
            "id": "LOT-TEST-99",
            "crop": "Pomegranate",
            "variety": "Bhagwa Export",
            "farmer_name": "Sanjay Patil",
            "farm_location": "Solapur, Maharashtra",
            "harvest_date": "2026-10-21",
            "quantity_tons": 18.0,
            "initial_temp": 26.0,
            "current_temp": 5.0,
            "target_temp": 5.0,
            "temp_safe": True,
            "humidity": 92.0,
            "shelf_life_days_total": 45,
            "shelf_life_remaining_days": 40,
            "grade": "A",
            "quality_score": 96,
            "cargo_health_score": 96,
            "status": "In-Transit",
            "mandi_rate_per_kg": 140.0,
            "escrow_secured_amount": 2520000.0,
            "subsidy_eligible": "PMKSY Grant",
            "sensor_verification_score": 100,
        }
        res_create = client.post("/api/v1/portals/farmer/batches", json=batch_payload)
        assert res_create.status_code == status.HTTP_201_CREATED

        res_list = client.get("/api/v1/portals/farmer/batches")
        assert res_list.status_code == status.HTTP_200_OK
        batches = res_list.json()
        assert any(b["id"] == "LOT-TEST-99" for b in batches)

    def test_mandi_rates_and_railway(self, client):
        res_mandi = client.get("/api/v1/portals/farmer/mandi-rates")
        assert res_mandi.status_code == status.HTTP_200_OK
        assert len(res_mandi.json()) > 0

        res_rail = client.get("/api/v1/portals/railway/trains")
        assert res_rail.status_code == status.HTTP_200_OK
        assert len(res_rail.json()) > 0

        res_insp = client.get("/api/v1/portals/inspections")
        assert res_insp.status_code == status.HTTP_200_OK
        assert "produce" in res_insp.json()


class TestAnalyticsEndpoints:
    """Test dashboard KPIs aggregation."""

    def test_dashboard_kpis(self, client):
        res = client.get("/api/v1/analytics/dashboard")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert "active_shipments" in data
        assert "critical_alerts" in data
        assert "fleet_active_count" in data
        assert "avg_temperature" in data
        assert "temp_compliance_pct" in data
        assert "total_co2_saved_kg" in data


class TestUserManagementEndpoints:
    """Test user listing and role updates with RBAC enforcement."""

    def test_list_and_update_user_role(self, client, db_session):
        from scripts.provision_admin import provision_admin

        # 1. Anonymous access is rejected with 401
        res_anon = client.get("/api/v1/auth/users")
        assert res_anon.status_code == status.HTTP_401_UNAUTHORIZED

        # 2. Register a standard user
        user_in = {
            "email": "agent.test@coldchain360.in",
            "password": "Password123!",
        }
        res_reg = client.post("/api/v1/auth/register", json=user_in)
        assert res_reg.status_code == status.HTTP_201_CREATED
        user_id = res_reg.json()["id"]

        # 3. Standard user access is rejected with 403 Forbidden
        res_login_user = client.post("/api/v1/auth/login", json=user_in)
        user_token = res_login_user.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

        res_forbidden = client.get("/api/v1/auth/users", headers=user_headers)
        assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

        res_forbidden_role = client.patch(
            f"/api/v1/auth/users/{user_id}/role",
            json={"role": "fleet_manager"},
            headers=user_headers,
        )
        assert res_forbidden_role.status_code == status.HTTP_403_FORBIDDEN

        # 4. Provision admin securely in database
        ok, msg, admin_id = provision_admin(
            "admin.domain@coldchain360.in",
            "AdminSecure123!",
            name="Domain Admin",
            db=db_session,
        )
        assert ok is True

        res_admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin.domain@coldchain360.in", "password": "AdminSecure123!"},
        )
        admin_token = res_admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 5. Verified admin successfully lists users
        res_list = client.get("/api/v1/auth/users", headers=admin_headers)
        assert res_list.status_code == status.HTTP_200_OK
        users = res_list.json()
        assert any(u["id"] == user_id for u in users)

        # 6. Verified admin successfully updates user role
        res_role = client.patch(
            f"/api/v1/auth/users/{user_id}/role",
            json={"role": "fleet_manager"},
            headers=admin_headers,
        )
        assert res_role.status_code == status.HTTP_200_OK
        assert res_role.json()["role"] == "fleet_manager"

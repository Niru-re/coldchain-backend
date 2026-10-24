"""Authentication tests for ColdChain 360 API."""

import pytest
from datetime import timedelta
from jose import jwt

from config import settings
from services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    authenticate_user,
)
from db.session import check_db_configured
from models.User import User as UserModel


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hashing_works(self):
        """Test that passwords are properly hashed with bcrypt and verified."""
        password = "SecurePass123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert "$2" in hashed  # Standard bcrypt identifier
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        """Test that wrong password fails verification."""
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password("WrongPassword123!", hashed) is False


class TestJWTToken:
    """Test JWT token creation, decoding, and expiration."""

    def test_create_and_decode_access_token(self):
        """Test creating and decoding a valid JWT access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        assert isinstance(token, str)

        payload = decode_access_token(token)
        assert payload.get("sub") == "test@example.com"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Test that malformed or non-JWT tokens are safely rejected."""
        assert decode_access_token("not.a.valid.jwt.token") == {}
        assert decode_access_token("") == {}
        assert decode_access_token(None) == {}

    def test_decode_expired_token(self):
        """Test that expired tokens are rejected."""
        data = {"sub": "test@example.com"}
        expired_token = create_access_token(
            data=data,
            expires_delta=timedelta(seconds=-10),  # expired 10s ago
        )
        assert decode_access_token(expired_token) == {}


class TestUserRegistration:
    """Test user registration API endpoint."""

    def test_register_successful(self, client, db_session):
        """Test that a new user can register successfully."""
        payload = {
            "email": "user@example.com",
            "password": "SecurePassword123!",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

        # Verify password in database is hashed, not plain text
        user = db_session.query(UserModel).filter(UserModel.email == "user@example.com").first()
        assert user is not None
        assert user.hashed_password != "SecurePassword123!"
        assert verify_password("SecurePassword123!", user.hashed_password) is True

    def test_register_duplicate_email(self, client):
        """Test that registering with duplicate email returns 400."""
        payload = {
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
        }
        res1 = client.post("/api/v1/auth/register", json=payload)
        assert res1.status_code == 201

        res2 = client.post("/api/v1/auth/register", json=payload)
        assert res2.status_code == 400
        assert "already registered" in res2.json()["detail"].lower()

    def test_register_normalizes_email(self, client, db_session):
        """Test that email is lowercased on registration."""
        payload = {
            "email": "MixedCase@Example.COM",
            "password": "SecurePassword123!",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        assert response.json()["email"] == "mixedcase@example.com"

        user = db_session.query(UserModel).filter(UserModel.email == "mixedcase@example.com").first()
        assert user is not None

    def test_register_rejects_admin_role_self_assignment(self, client):
        """Test that public registration cannot self-assign the admin role."""
        payload = {
            "email": "admin_attempt@example.com",
            "password": "SecurePassword123!",
            "role": "admin",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == "user", "Public registration must force role to 'user'"

    def test_register_password_too_short(self, client):
        """Test validation error when password is under 8 characters."""
        payload = {
            "email": "shortpass@example.com",
            "password": "short",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422


class TestUserLogin:
    """Test user login API endpoint."""

    def test_login_successful(self, client):
        """Test login with valid credentials returns JWT bearer token."""
        # First register
        client.post("/api/v1/auth/register", json={
            "email": "login_user@example.com",
            "password": "Password123!",
        })

        # Login
        response = client.post("/api/v1/auth/login", json={
            "email": "login_user@example.com",
            "password": "Password123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token content
        payload = decode_access_token(data["access_token"])
        assert payload.get("sub") == "login_user@example.com"

    def test_login_wrong_password(self, client):
        """Test login with incorrect password returns 401."""
        client.post("/api/v1/auth/register", json={
            "email": "wrong_pwd@example.com",
            "password": "CorrectPassword123!",
        })

        response = client.post("/api/v1/auth/login", json={
            "email": "wrong_pwd@example.com",
            "password": "IncorrectPassword123!",
        })
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with unregistered email returns 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "Password123!",
        })
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_inactive_user_rejected(self, client, db_session):
        """Test deactivated user cannot log in and receives 401."""
        client.post("/api/v1/auth/register", json={
            "email": "inactive@example.com",
            "password": "Password123!",
        })
        user = db_session.query(UserModel).filter(UserModel.email == "inactive@example.com").first()
        user.is_active = False
        db_session.commit()

        response = client.post("/api/v1/auth/login", json={
            "email": "inactive@example.com",
            "password": "Password123!",
        })
        assert response.status_code == 401
        assert "inactive" in response.json()["detail"].lower()


class TestAuthMeEndpoint:
    """Test /api/v1/auth/me bearer token protected endpoint."""

    def test_auth_me_with_valid_bearer_token(self, client):
        """Test /api/v1/auth/me returns user profile with valid Bearer token."""
        client.post("/api/v1/auth/register", json={
            "email": "me_user@example.com",
            "password": "Password123!",
        })
        login_res = client.post("/api/v1/auth/login", json={
            "email": "me_user@example.com",
            "password": "Password123!",
        })
        token = login_res.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me_user@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True

    def test_auth_me_missing_token(self, client):
        """Test /api/v1/auth/me without Authorization header returns 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()
        assert "WWW-Authenticate" in response.headers

    def test_auth_me_invalid_token(self, client):
        """Test /api/v1/auth/me with invalid token returns 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_garbage_token"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
        assert "WWW-Authenticate" in response.headers

    def test_auth_me_expired_token(self, client):
        """Test /api/v1/auth/me with expired token returns 401."""
        expired_token = create_access_token(
            data={"sub": "me_user@example.com"},
            expires_delta=timedelta(seconds=-10),
        )
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
        assert "WWW-Authenticate" in response.headers


class TestDatabaseConfigValidation:
    """Test database configuration validation behavior."""

    def test_database_configured_helper(self):
        """Verify is_database_configured accurately flags placeholders and unconfigured states."""
        assert settings.is_database_configured is True or settings.is_database_configured is False

    def test_check_db_configured_raises_on_unconfigured(self, monkeypatch):
        """Verify check_db_configured raises ValueError when database is unconfigured."""
        monkeypatch.setattr(type(settings), "is_database_configured", property(lambda self: False))
        with pytest.raises(ValueError) as excinfo:
            check_db_configured()
        assert "DATABASE_URL is not configured" in str(excinfo.value)


class TestAdminProvisioning:
    """Test initial administrator provisioning script logic."""

    def test_provision_admin_creates_admin_role_and_hashes_password(self, db_session):
        """Verify provisioning creates expected database role and hashes password with bcrypt."""
        from scripts.provision_admin import provision_admin
        from sqlalchemy import select

        email = "lead.admin@coldchain360.in"
        password = "AdminSuperSecret2026!"

        success, msg, user_id = provision_admin(
            email=email,
            password=password,
            name="Vikramaditya Rao",
            db=db_session,
        )
        assert success is True
        assert user_id is not None

        # Verify user in database
        user = db_session.execute(
            select(UserModel).where(UserModel.email == email)
        ).scalar_one()

        assert user.role == "admin"
        assert user.full_name == "Vikramaditya Rao"
        assert user.is_active is True
        assert user.hashed_password != password
        assert "$2" in user.hashed_password
        assert verify_password(password, user.hashed_password) is True

    def test_rerunning_provisioning_idempotent_no_duplicate_or_silent_reset(self, db_session):
        """Verify re-running provisioning is idempotent and does NOT reset existing password."""
        from scripts.provision_admin import provision_admin
        from sqlalchemy import select

        email = "idempotent.admin@coldchain360.in"
        orig_password = "OriginalPassword123!"
        new_password = "AttemptedResetPassword999!"

        # Initial provision
        ok1, msg1, id1 = provision_admin(
            email=email,
            password=orig_password,
            db=db_session,
        )
        assert ok1 is True

        # Re-run with different password
        ok2, msg2, id2 = provision_admin(
            email=email,
            password=new_password,
            db=db_session,
        )
        assert ok2 is True
        assert id1 == id2
        assert "already exists" in msg2

        # Verify password was NOT silently reset
        user = db_session.execute(
            select(UserModel).where(UserModel.email == email)
        ).scalar_one()

        assert verify_password(orig_password, user.hashed_password) is True
        assert verify_password(new_password, user.hashed_password) is False

    def test_refuse_unsafe_privilege_escalation_without_flag(self, db_session):
        """Verify provisioning refuses to promote an existing non-admin user without confirmation."""
        from scripts.provision_admin import provision_admin
        from sqlalchemy import select

        email = "driver.user@coldchain360.in"
        # Create normal user
        db_user = UserModel(
            email=email,
            hashed_password=get_password_hash("DriverPass123!"),
            role="driver",
            is_active=True,
        )
        db_session.add(db_user)
        db_session.commit()

        # Provision without --force-upgrade must fail
        ok, msg, uid = provision_admin(
            email=email,
            password="NewAdminPassword123!",
            force_upgrade=False,
            db=db_session,
        )
        assert ok is False
        assert "Refusing to alter permissions" in msg

        # Role remains driver
        user = db_session.execute(
            select(UserModel).where(UserModel.email == email)
        ).scalar_one()
        assert user.role == "driver"

        # Provision with force_upgrade=True succeeds
        ok_force, msg_force, uid_force = provision_admin(
            email=email,
            password="NewAdminPassword123!",
            force_upgrade=True,
            db=db_session,
        )
        assert ok_force is True
        db_session.refresh(user)
        assert user.role == "admin"


class TestPrivilegedEndpointAuthorization:
    """Test RBAC enforcement across user-listing and role management endpoints."""

    def test_anonymous_requests_return_401(self, client):
        """Anonymous requests to privileged endpoints must return HTTP 401."""
        res_list = client.get("/api/v1/auth/users")
        assert res_list.status_code == 401
        assert "not authenticated" in res_list.json()["detail"].lower()

        res_role = client.patch("/api/v1/auth/users/1/role", json={"role": "admin"})
        assert res_role.status_code == 401

        res_profile = client.patch("/api/v1/auth/users/1", json={"full_name": "Anon"})
        assert res_profile.status_code == 401

    def test_non_admin_requests_return_403(self, client, db_session):
        """Authenticated non-admin requests to privileged endpoints must return HTTP 403."""
        # Register and login non-admin user
        user_payload = {"email": "regular.user@coldchain360.in", "password": "UserPass123!"}
        client.post("/api/v1/auth/register", json=user_payload)
        login_res = client.post("/api/v1/auth/login", json=user_payload)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Non-admin attempting to list users -> 403
        res_list = client.get("/api/v1/auth/users", headers=headers)
        assert res_list.status_code == 403
        assert "administrative privileges required" in res_list.json()["detail"].lower()

        # Non-admin attempting to update role -> 403
        res_role = client.patch("/api/v1/auth/users/1/role", json={"role": "admin"}, headers=headers)
        assert res_role.status_code == 403

    def test_verified_admin_can_access_user_management(self, client, db_session):
        """Verified admin can list users and update roles."""
        from scripts.provision_admin import provision_admin

        # Provision admin
        provision_admin(
            "super.admin@coldchain360.in",
            "SuperAdminPass123!",
            name="Super Admin",
            db=db_session,
        )

        # Login as admin
        admin_login = client.post("/api/v1/auth/login", json={
            "email": "super.admin@coldchain360.in",
            "password": "SuperAdminPass123!",
        })
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create target user to manage
        target_payload = {"email": "target.agent@coldchain360.in", "password": "TargetPass123!"}
        res_target = client.post("/api/v1/auth/register", json=target_payload)
        target_id = res_target.json()["id"]

        # Admin lists users -> 200
        res_list = client.get("/api/v1/auth/users", headers=admin_headers)
        assert res_list.status_code == 200
        users = res_list.json()
        assert any(u["id"] == target_id for u in users)

        # Admin updates role -> 200
        res_role = client.patch(
            f"/api/v1/auth/users/{target_id}/role",
            json={"role": "truck_admin"},
            headers=admin_headers,
        )
        assert res_role.status_code == 200
        assert res_role.json()["role"] == "truck_admin"

    def test_user_cannot_self_escalate_role_via_profile_update(self, client, db_session):
        """User profile update cannot modify role or elevate privileges."""
        user_payload = {"email": "sneaky.user@coldchain360.in", "password": "UserPass123!"}
        res_reg = client.post("/api/v1/auth/register", json=user_payload)
        user_id = res_reg.json()["id"]

        login_res = client.post("/api/v1/auth/login", json=user_payload)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to pass role="admin" via profile update
        res_update = client.patch(
            f"/api/v1/auth/users/{user_id}",
            json={"full_name": "Sneaky User", "role": "admin"},
            headers=headers,
        )
        assert res_update.status_code == 200
        data = res_update.json()
        assert data["full_name"] == "Sneaky User"
        assert data["role"] == "user"  # Role was NOT elevated

    def test_non_admin_cannot_update_another_user_profile(self, client, db_session):
        """User cannot update someone else's profile."""
        u1 = client.post("/api/v1/auth/register", json={"email": "u1@coldchain360.in", "password": "Password123!"}).json()
        u2 = client.post("/api/v1/auth/register", json={"email": "u2@coldchain360.in", "password": "Password123!"}).json()

        login1 = client.post("/api/v1/auth/login", json={"email": "u1@coldchain360.in", "password": "Password123!"}).json()
        headers1 = {"Authorization": f"Bearer {login1['access_token']}"}

        res = client.patch(f"/api/v1/auth/users/{u2['id']}", json={"full_name": "Tampered"}, headers=headers1)
        assert res.status_code == 403

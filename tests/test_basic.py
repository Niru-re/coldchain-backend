"""Basic API tests for ColdChain 360 backend."""

from app import app


def test_openapi_schema():
    """Verify OpenAPI schema structure and metadata."""
    openapi_schema = app.openapi()
    assert openapi_schema is not None
    assert isinstance(openapi_schema, dict)
    assert openapi_schema["info"]["title"] == "ColdChain 360 API"
    assert openapi_schema["info"]["version"] == "1.0.0"


def test_route_registration():
    """Verify required API routes are registered with correct prefixes."""
    openapi_schema = app.openapi()
    paths = list(openapi_schema["paths"].keys())

    # Exact expected routes
    assert "/api/v1/auth/register" in paths, "Missing /api/v1/auth/register route"
    assert "/api/v1/auth/login" in paths, "Missing /api/v1/auth/login route"
    assert "/api/v1/auth/me" in paths, "Missing /api/v1/auth/me route"
    assert "/" in paths, "Missing / route"
    assert "/health" in paths, "Missing /health route"
    assert "/health/db" in paths, "Missing /health/db route"

    # Verify NO duplicated /api/v1/api/v1/ routes exist
    duplicated_routes = [p for p in paths if "/api/v1/api/v1" in p]
    assert len(duplicated_routes) == 0, f"Found duplicated prefix routes: {duplicated_routes}"


def test_root_endpoint(client):
    """Test root endpoint returns 200 with service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ColdChain 360 API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test health check endpoint returns 200 healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "coldchain-360-api"
    assert data["version"] == "1.0.0"


def test_database_health_endpoint_response_format(client):
    """Test that /health/db returns structured status information without crashing."""
    response = client.get("/health/db")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] in ("healthy", "unhealthy")


def test_database_health_unconfigured(client, monkeypatch):
    """Test that /health/db returns 503 with unconfigured status when database is unconfigured."""
    from config import settings
    monkeypatch.setattr(type(settings), "is_database_configured", property(lambda self: False))
    response = client.get("/health/db")
    assert response.status_code == 503
    data = response.json()
    assert data["database"] == "unconfigured"
    assert data["status"] == "unhealthy"
    assert "not configured" in data["message"].lower()


def test_database_health_unavailable(client, monkeypatch):
    """Test that /health/db returns 503 with sanitized message when connection fails."""
    import app as app_module
    from sqlalchemy.exc import OperationalError

    class FailingEngine:
        def connect(self):
            raise OperationalError("FATAL: connection timeout", params=None, orig=Exception("secret_password_here"))

    monkeypatch.setattr(app_module, "engine", FailingEngine())
    response = client.get("/health/db")
    assert response.status_code == 503
    data = response.json()
    assert data["database"] == "unavailable"
    assert data["status"] == "unhealthy"
    assert "failed" in data["message"].lower() or "unreachable" in data["message"].lower()
    # Ensure no internal error strings or passwords leaked
    assert "secret_password_here" not in str(data)

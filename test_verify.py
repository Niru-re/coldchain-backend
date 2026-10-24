"""Verify backend configuration and API."""
import sys
from pathlib import Path

# Ensure backend directory is in path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
_orig_httpx_init = httpx.Client.__init__
def _compat_httpx_init(self, *args, **kwargs):
    kwargs.pop("app", None)
    return _orig_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = _compat_httpx_init

from config import settings
print("SECRET_KEY:", "SET" if settings.SECRET_KEY and settings.SECRET_KEY != "dev-secret-key-change-in-production" else "USING DEFAULT - CHANGE FOR PRODUCTION")
print("DATABASE_CONFIGURED:", settings.is_database_configured)
print("DEBUG:", settings.DEBUG)
print("BCRYPT_ROUNDS:", settings.BCRYPT_ROUNDS)
print("API_V1_STR:", settings.API_V1_STR)

from app import app
print("FastAPI app imported successfully")
print("App title:", app.title)

from fastapi.testclient import TestClient
client = TestClient(app)
resp = client.get("/")
print("GET / status:", resp.status_code)
print("GET / response:", resp.json())

resp = client.get("/health")
print("GET /health status:", resp.status_code)
print("GET /health response:", resp.json())

resp = client.get("/health/db")
print("GET /health/db status:", resp.status_code)
print("GET /health/db response:", resp.json())

routes = [route.path for route in app.routes]
api_routes = [r for r in routes if "/api/v1/" in r]
print("API v1 routes registered:", len(api_routes))
for r in api_routes[:5]:
    print("  -", r)
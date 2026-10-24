"""Main application entry point for ColdChain 360 API."""

import sys
from pathlib import Path

# Ensure the backend directory is in the Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.session import get_db, engine, SessionLocal
from config import settings
from routes.auth import router as auth_router
from routes.shipments import router as shipments_router
from routes.fleet import router as fleet_router
from routes.alerts import router as alerts_router
from routes.warehouses import router as warehouses_router
from routes.portals import router as portals_router
from routes.analytics import router as analytics_router
from routes.intelligence import router as intelligence_router

# Initialize FastAPI app
app = FastAPI(
    title="ColdChain 360 API",
    description="Backend API for ColdChain 360 logistics platform",
    version="1.0.0",
)

# Configure CORS using environment settings and production deployment domains
cors_origins = [
    origin.strip() for origin in settings.BACKEND_CORS_ORIGINS if origin.strip()
]
for dev_origin in [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
]:
    if dev_origin not in cors_origins:
        cors_origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if "*" not in cors_origins else ["*"],
    allow_origin_regex=r"^https?://.*" if "*" in cors_origins else r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.netlify\.app|.*\.onrender\.com)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(shipments_router, prefix="/api/v1")
app.include_router(fleet_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(warehouses_router, prefix="/api/v1")
app.include_router(portals_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Basic API information endpoint."""
    return {
        "message": "ColdChain 360 API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Application operational health check endpoint.

    Reports the application server status without querying or falsely
    implying database connectivity.
    """
    return {
        "status": "healthy",
        "service": "coldchain-360-api",
        "version": "1.0.0",
    }


@app.get("/health/db", tags=["Health"])
async def health_db():
    """Safe database connectivity check endpoint.

    Executes a safe, lightweight query (SELECT 1) using the configured backend engine.
    Returns HTTP 200 with status: healthy when the database is reachable.
    Returns HTTP 503 with status: unhealthy when unconfigured or unreachable.
    Never exposes internal credentials, connection strings, or internal errors.
    """
    if not settings.is_database_configured:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "database": "unconfigured",
                "status": "unhealthy",
                "message": "DATABASE_URL is not configured or contains placeholder credentials.",
            },
        )
    try:
        # Execute a safe query with a short connection timeout to verify database connectivity
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "status": "healthy",
        }
    except Exception:
        # Return sanitized error message without exposing connection details or stack trace
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "database": "unavailable",
                "status": "unhealthy",
                "message": "Database connection failed or service is unreachable.",
            },
        )
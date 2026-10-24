"""Pytest fixtures and configuration for ColdChain 360 backend tests."""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory and project root are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# TestClient compatibility shim for starlette 0.35 + httpx 0.28+
import httpx
_orig_httpx_init = httpx.Client.__init__


def _compat_httpx_init(self, *args, **kwargs):
    app = kwargs.pop("app", None)
    if app is not None and "transport" not in kwargs:
        kwargs["transport"] = httpx.ASGITransport(app=app)
    return _orig_httpx_init(self, *args, **kwargs)


httpx.Client.__init__ = _compat_httpx_init

from db.base import Base
from db.session import get_db
import models
from app import app
from fastapi.testclient import TestClient

# Isolated SQLite in-memory test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, future=True
)


def override_get_db():
    """Dependency override providing an isolated test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all database tables once for the test session."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    """Provide a transactional database session rolled back after each test."""
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Provide a TestClient with overridden get_db dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

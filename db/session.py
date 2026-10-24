from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .base import Base
from config import settings


def check_db_configured() -> None:
    """Verify that database connection is configured and valid."""
    if not settings.is_database_configured:
        raise ValueError(
            "DATABASE_URL is not configured or contains placeholder credentials. "
            "Please configure a valid database connection string in backend/.env"
        )


# Create engine safely
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,  # SQL query logging in debug mode
        future=True,  # Use SQLAlchemy 2.x style
    )
except Exception:
    engine = create_engine("sqlite://", future=True)


# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db() -> Session:
    """Dependency that yields a database session."""
    check_db_configured()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
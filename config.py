import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the backend directory (parent of this file)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)


class Settings:
    """Application settings loaded from environment variables."""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ColdChain 360 API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-in-production":
        # In production, this should be caught, but allow development
        pass
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/coldchain",
    )

    @property
    def is_database_configured(self) -> bool:
        """Check whether DATABASE_URL is configured and not a placeholder."""
        raw_url = os.getenv("DATABASE_URL", "").strip()
        if not raw_url:
            return False
        if "PLACEHOLDER" in raw_url or "xxx.supabase.co" in raw_url:
            return False
        return True

    # CORS
    BACKEND_CORS_ORIGINS: list = (
        os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        .split(",")
        if os.getenv("BACKEND_CORS_ORIGINS")
        else ["http://localhost:5173"]
    )

    # Password hashing
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))


settings = Settings()
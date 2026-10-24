from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt as j_wt

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    pwd_context = None

from models.User import User as UserModel
from schemas.User import UserCreate, UserLogin, UserResponse
from db.session import get_db
from config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if not plain_password or not hashed_password:
        return False
    if pwd_context is not None:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    try:
        import bcrypt
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    if pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    import bcrypt
    rounds = settings.BCRYPT_ROUNDS if hasattr(settings, "BCRYPT_ROUNDS") else 12
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def authenticate_user(db, email: str, password: str):
    """Authenticate a user against the database.
    
    Email is normalized (lowercased, stripped) for case-insensitive lookup.
    """
    from sqlalchemy import select, func
    from models.User import User as UserModel

    if not email or not password:
        return False

    clean_email = email.lower().strip()
    user = db.execute(
        select(UserModel).where(func.lower(UserModel.email) == clean_email)
    ).scalar_one_or_none()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = j_wt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token."""
    if not token or not isinstance(token, str):
        return {}
    try:
        payload = j_wt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except (JWTError, Exception):
        return {}


def get_current_user(
    token: str,
    db,
) -> UserModel:
    """Get the current user from a JWT token."""
    from sqlalchemy import select
    from models.User import User as UserModel

    payload = decode_access_token(token)
    if payload is None:
        return None

    email: str = payload.get("sub")
    if email is None:
        return None

    user = db.execute(select(UserModel).where(UserModel.email == email)).scalar_one_or_none()
    if user is None:
        return None

    if not user.is_active:
        return None

    return user
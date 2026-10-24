from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.session import get_db
from services.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from schemas.User import UserCreate, UserLogin, UserResponse, UserUpdate, UserRoleUpdate
from models.User import User as UserModel


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


def get_current_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    """Extract and validate bearer token from Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_current_user(credentials.credentials, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """Ensure the authenticated user holds the admin role in the database."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required",
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    - Public registration must not permit admin role self-assignment.
    - Email is normalized (lowercased) and validated for uniqueness.
    - Password is hashed before storage.
    """
    from sqlalchemy import select

    # Normalize email to lowercase
    email = user_in.email.lower().strip()

    # Check for existing user
    existing = db.execute(select(UserModel).where(UserModel.email == email)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = get_password_hash(user_in.password)

    # Default role is "user" for public registration — never admin
    db_user = UserModel(
        email=email,
        hashed_password=hashed_password,
        role="user",  # Public registration always gets "user" role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        role=db_user.role,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
    )


@router.post("/login", response_model=dict)
async def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Login user and receive JWT access token.

    - Credentials are validated against the database.
    - On success, returns signed JWT access token.
    - On failure, returns suitable HTTP error.
    """
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get current user profile (requires authentication).

    - Protected by JWT bearer authentication dependency.
    - Returns user info without password hash.
    """
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all registered system users (admin only)."""
    from sqlalchemy import select
    stmt = select(UserModel).order_by(UserModel.id.asc())
    return db.execute(stmt).scalars().all()


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_in: UserRoleUpdate,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update role for a specified user (admin only)."""
    from sqlalchemy import select
    user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    user.role = role_in.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update user profile fields.
    
    Users can update their own profile; admins can update any profile.
    Self-promotion and role escalation are strictly prevented.
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update another user's profile",
        )

    from sqlalchemy import select
    user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    updates = user_in.model_dump(exclude_unset=True)
    # Strictly strip any role or password modification from general profile update
    updates.pop("role", None)
    updates.pop("hashed_password", None)

    # Only admins can alter account active state or clearance level
    if current_user.role != "admin":
        updates.pop("is_active", None)
        updates.pop("clearance_level", None)

    for field, val in updates.items():
        setattr(user, field, val)
    db.commit()
    db.refresh(user)
    return user

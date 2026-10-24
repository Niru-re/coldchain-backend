from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(
        ...,
        description="User's email address (must be unique)",
        json_schema_extra={"example": "user@example.com"},
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's password (minimum 8 characters)",
        json_schema_extra={"example": "SecurePass123!"},
    )
    role: Optional[str] = Field(
        default="user",
        description="User role (user, admin, dispatcher, fleet_manager, truck_admin, railway_admin, warehouse_admin, driver, farmer, customer)",
    )
    full_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None
    clearance_level: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None
    clearance_level: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    """Schema for admin role updates."""
    role: str = Field(..., description="New role for the user")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        json_schema_extra={"example": "user@example.com"},
    )
    password: str = Field(
        ...,
        description="User's password",
        json_schema_extra={"example": "SecurePass123!"},
    )


class UserResponse(BaseModel):
    """Schema for user response (excluding sensitive data)."""

    id: int
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None
    clearance_level: Optional[str] = None
    assigned_vehicle_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    """Schema for public user info (no password hash)."""

    id: int
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    organization: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

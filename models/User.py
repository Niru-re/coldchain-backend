from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)

from db.base import Base


class User(Base):
    """User model representing authenticated users in the system."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password = Column(
        String,
        nullable=False,
    )
    role = Column(
        String,
        default="user",
        nullable=False,
    )
    full_name = Column(
        String,
        nullable=True,
    )
    phone = Column(
        String,
        nullable=True,
    )
    organization = Column(
        String,
        nullable=True,
    )
    location = Column(
        String,
        nullable=True,
    )
    avatar = Column(
        String,
        nullable=True,
    )
    clearance_level = Column(
        String,
        nullable=True,
    )
    assigned_vehicle_id = Column(
        String,
        nullable=True,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User email={self.email!r} id={self.id!r}>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == "admin"

    @property
    def is_superuser(self) -> bool:
        """Check if user is a superuser."""
        return self.role in ("admin", "superuser")
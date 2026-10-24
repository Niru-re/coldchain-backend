"""Driver model for fleet personnel."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func, ForeignKey
from db.base import Base


class Driver(Base):
    """Represents drivers operating cold-chain transport vehicles."""

    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False, index=True)
    license_number = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    status = Column(String, default="Available", nullable=False, index=True)  # Available, On Trip, Off Duty, Resting
    assigned_vehicle_id = Column(String, nullable=True)
    experience_years = Column(Float, default=3.0, nullable=False)
    rating = Column(Float, default=4.8, nullable=False)
    total_trips = Column(Integer, default=0, nullable=False)
    emergency_contact = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Driver name={self.name!r} license={self.license_number!r}>"

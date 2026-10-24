"""Truck and FleetVehicle model for cold-chain transport fleet."""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from db.base import Base


class Truck(Base):
    """Represents refrigerated fleet vehicles (trucks, reefer vans, intermodal units)."""

    __tablename__ = "trucks"

    id = Column(String, primary_key=True, index=True)  # e.g., 'CC-REEFER-01' or plate
    plate_number = Column(String, unique=True, index=True, nullable=False)
    vehicle_type = Column(
        String,
        default="Heavy Reefer 32T",
        nullable=False,
    )  # Heavy Reefer 32T, Electric Urban Reefer, Dual-Zone Intermodal, Pharma-Grade Cryo Carrier
    driver_name = Column(String, nullable=True)
    driver_id = Column(Integer, nullable=True, index=True)
    status = Column(
        String,
        default="Standby",
        nullable=False,
        index=True,
    )  # En Route, Docking, Standby, Maintenance Required
    reefer_health_score = Column(Integer, default=95, nullable=False)  # 0-100
    fuel_level = Column(Integer, default=100, nullable=False)  # 0-100%
    current_cargo = Column(String, nullable=True)
    compressor_pressure_psi = Column(Float, default=165.0, nullable=False)
    refrigerant_level_pct = Column(Integer, default=98, nullable=False)
    current_location = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    current_temperature = Column(Float, nullable=True)
    target_temperature = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Truck id={self.id!r} plate={self.plate_number!r} status={self.status!r}>"

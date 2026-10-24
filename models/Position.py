"""Position and Telematics model for GPS breadcrumbs and sensor history."""

from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from db.base import Base


class Position(Base):
    """Represents a discrete GPS and environmental sensor ping for a shipment or vehicle."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=True, index=True)
    truck_id = Column(String, ForeignKey("trucks.id", ondelete="CASCADE"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=0.0, nullable=False)
    heading_deg = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)  # Cargo compartment temp
    ambient_temp = Column(Float, nullable=True)  # Outside ambient temp
    humidity = Column(Float, nullable=True)      # Humidity percentage
    battery_level = Column(Integer, nullable=True)
    door_status = Column(String, default="Sealed", nullable=True)
    reefer_status = Column(String, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Position shipment={self.shipment_id!r} lat={self.latitude} lon={self.longitude}>"

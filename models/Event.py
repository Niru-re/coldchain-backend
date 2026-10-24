"""Event and milestone history model for shipments."""

from sqlalchemy import Column, Integer, String, Float, DateTime, func, ForeignKey
from db.base import Base


class Event(Base):
    """Represents an operational milestone, status change, or audit event in a shipment journey."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)  # Departure, Arrival, Checkpoint, Temp Excursion, Door Open, Inspection
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    severity = Column(String, default="info", nullable=False)  # info, warning, critical
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Event id={self.id} shipment={self.shipment_id!r} type={self.event_type!r}>"

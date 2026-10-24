"""Assignment model connecting shipments, trucks, and drivers."""

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from db.base import Base


class Assignment(Base):
    """Represents an operational assignment linking a shipment, truck, and driver."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    truck_id = Column(String, ForeignKey("trucks.id", ondelete="SET NULL"), nullable=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String, default="Assigned", nullable=False, index=True)  # Assigned, In Progress, Completed, Cancelled
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Assignment id={self.id!r} shipment={self.shipment_id!r} truck={self.truck_id!r}>"

"""Alert model for critical cold-chain excursions and system notifications."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    func,
    ForeignKey,
)
from db.base import Base


class Alert(Base):
    """Represents an active or resolved incident alert."""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)  # e.g., 'ALT-8849-01'
    shipment_id = Column(String, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=True, index=True)
    truck_id = Column(String, ForeignKey("trucks.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type = Column(
        String,
        default="Temperature Excursion",
        nullable=False,
        index=True,
    )  # Temperature Excursion, Shelf Life Risk, Door Tamper, Compressor Fault, Route Deviation, Delay
    severity = Column(
        String,
        default="warning",
        nullable=False,
        index=True,
    )  # info, warning, critical
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    predicted_excursion_time = Column(String, nullable=True)
    predicted_loss_usd = Column(String, nullable=True)
    recommended_actions = Column(JSON, default=list, nullable=False)

    is_acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    is_resolved = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(String, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Alert id={self.id!r} severity={self.severity!r} title={self.title!r}>"

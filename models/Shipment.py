"""Shipment model for canonical hybrid cold-chain logistics consignments."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    func,
    ForeignKey,
)
from db.base import Base


class Shipment(Base):
    """Represents end-to-end multi-modal cold-chain consignments."""

    __tablename__ = "shipments"

    id = Column(String, primary_key=True, index=True)  # e.g., 'CC-1048'
    tracking_number = Column(String, unique=True, index=True, nullable=False)
    commodity = Column(String, nullable=False, index=True)
    category = Column(
        String,
        default="Fresh Produce",
        nullable=False,
        index=True,
    )  # Pharmaceuticals, Dairy, Fresh Produce, Seafood, Biologics, Frozen Foods
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    current_location = Column(String, nullable=True)
    carrier = Column(String, default="ColdChain 360 Express", nullable=False)
    mode = Column(String, default="Road", nullable=False)  # Road, Rail, Air, Multimodal
    status = Column(
        String,
        default="In Transit",
        nullable=False,
        index=True,
    )  # In Transit, Critical Alert, Rerouted, Delivered, Quarantined

    # Cold-chain sensor telemetry & thresholds
    temperature = Column(Float, nullable=False)  # Current reading (°C)
    min_temp = Column(Float, nullable=False)      # Min threshold (°C)
    max_temp = Column(Float, nullable=False)      # Max threshold (°C)
    humidity = Column(Float, default=85.0, nullable=False)  # Relative humidity (%)
    battery_level = Column(Integer, default=95, nullable=False)  # Sensor/IoT battery (%)
    reefer_status = Column(
        String,
        default="Active & Optimal",
        nullable=False,
    )  # Active & Optimal, Eco Mode, Defrosting Cycle, Compressor Warning, Critical Failure
    door_status = Column(String, default="Sealed & Locked", nullable=False)  # Sealed & Locked, Open, Tamper Detected
    gps_signal = Column(String, default="Strong (5G/LEO)", nullable=False)  # Strong (5G/LEO), Degraded, Offline Mesh

    # Risk & Shelf-life intelligence
    risk_score = Column(Integer, default=10, nullable=False)  # 0-100
    risk_level = Column(String, default="Nominal", nullable=False)  # Nominal, Guarded, Elevated, Critical
    remaining_shelf_life_hours = Column(Float, default=72.0, nullable=False)
    initial_shelf_life_hours = Column(Float, default=72.0, nullable=False)
    eta = Column(String, nullable=True)
    original_eta = Column(String, nullable=True)
    shock_g = Column(Float, default=0.05, nullable=False)
    light_lux = Column(Integer, default=0, nullable=False)

    # Commercial & ESG fields
    farmer_producer = Column(String, nullable=True)
    economic_value = Column(String, nullable=True)  # e.g., '$48,500' or '₹38,00,000'
    co2_saved_kg = Column(Integer, default=0, nullable=False)

    # Relationships & Linked Entities
    truck_id = Column(String, ForeignKey("trucks.id", ondelete="SET NULL"), nullable=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Detailed Structured Payloads (waypoints, historical telematics & AI alerts)
    waypoints = Column(JSON, default=list, nullable=False)
    temperature_history = Column(JSON, default=list, nullable=False)
    ai_alert = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Shipment id={self.id!r} tracking={self.tracking_number!r} status={self.status!r}>"

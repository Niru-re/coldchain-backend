"""Operational rules model for automated cold-chain triggers."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from db.base import Base


class OperationalRule(Base):
    """Represents policy rules for telematics, door breach, and temperature excursion thresholds."""

    __tablename__ = "operational_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    rule_type = Column(String, nullable=False, index=True)  # Temperature, Route, Door, Battery, ShelfLife
    category = Column(String, default="All", nullable=False)
    condition_parameter = Column(String, nullable=False)  # e.g., 'temperature', 'door_open_minutes', 'route_deviation_km'
    operator = Column(String, default=">", nullable=False)  # >, <, >=, <=, ==, !=
    threshold_value = Column(Float, nullable=False)
    action = Column(String, nullable=False)  # e.g., 'dispatch_rescue', 'alert_driver', 'reroute_hub'
    severity = Column(String, default="critical", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<OperationalRule name={self.name!r} type={self.rule_type!r}>"

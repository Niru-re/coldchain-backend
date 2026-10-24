"""Warehouse and Cold Storage Chamber models."""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from db.base import Base


class WarehouseNode(Base):
    """Represents a regional cold storage logistics terminal or node."""

    __tablename__ = "warehouse_nodes"

    id = Column(String, primary_key=True, index=True)  # e.g., 'WH-BOM-01'
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    zone = Column(String, default="Cold Zone A", nullable=False)
    current_temp = Column(Float, nullable=False)
    target_temp = Column(Float, nullable=False)
    capacity_used_percentage = Column(Integer, default=75, nullable=False)
    pallet_count = Column(Integer, default=1200, nullable=False)
    max_pallets = Column(Integer, default=1500, nullable=False)
    risk_status = Column(String, default="Optimal", nullable=False)  # Optimal, Caution, Excursion Warning
    expiring_lots_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<WarehouseNode id={self.id!r} name={self.name!r}>"


class WarehouseChamber(Base):
    """Represents an individual refrigerated chamber or CA atmosphere room inside a facility."""

    __tablename__ = "warehouse_chambers"

    chamber_id = Column(String, primary_key=True, index=True)  # e.g., 'CH-01'
    warehouse_id = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    chamber_type = Column(
        String,
        default="Chilled Cold Room",
        nullable=False,
    )  # Deep Freeze, Chilled Cold Room, Controlled Atmosphere (CA), Blast Freezer Tunnel
    temperature = Column(Float, nullable=False)
    target_temp = Column(Float, nullable=False)
    humidity_rh = Column(Float, default=90.0, nullable=False)
    target_humidity_rh = Column(Float, default=90.0, nullable=False)
    gas_o2_percent = Column(Float, nullable=True)
    gas_co2_percent = Column(Float, nullable=True)
    pallet_capacity = Column(Integer, default=500, nullable=False)
    occupied_pallets = Column(Integer, default=350, nullable=False)
    refrigerant_status = Column(String, default="Optimal · Freon R404A", nullable=False)
    ammonia_ppm = Column(Float, default=0.0, nullable=False)
    status = Column(String, default="Active", nullable=False)  # Active, Pre-Cooling, Defrosting, Maintenance
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<WarehouseChamber id={self.chamber_id!r} name={self.name!r}>"

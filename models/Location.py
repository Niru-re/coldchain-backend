"""Location model for facilities, farms, hubs, and distribution centers."""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from db.base import Base


class Location(Base):
    """Represents physical locations such as farms, hubs, warehouses, and terminals."""

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, index=True, nullable=True)
    location_type = Column(String, default="Hub", nullable=False)  # Farm, Truck, Hub, Rail, Airport, Warehouse, Buyer
    address = Column(String, nullable=True)
    city = Column(String, nullable=True, index=True)
    state = Column(String, nullable=True, index=True)
    country = Column(String, default="India", nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity_pallets = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Location name={self.name!r} type={self.location_type!r}>"

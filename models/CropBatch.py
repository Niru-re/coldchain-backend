"""CropBatch and Farmer Consignment model."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from db.base import Base


class CropBatch(Base):
    """Represents harvest batches registered by farmers and cooperatives."""

    __tablename__ = "crop_batches"

    id = Column(String, primary_key=True, index=True)  # e.g., 'BATCH-MH-MNG-991'
    crop = Column(String, nullable=False, index=True)
    variety = Column(String, nullable=False)
    farmer_name = Column(String, nullable=False, index=True)
    farm_location = Column(String, nullable=False)
    harvest_date = Column(String, nullable=False)
    dispatch_time = Column(String, nullable=True)
    target_buyer = Column(String, nullable=True)
    buyer_location = Column(String, nullable=True)
    quantity_tons = Column(Float, nullable=False)
    initial_temp = Column(Float, default=24.0, nullable=False)
    current_temp = Column(Float, default=4.5, nullable=False)
    target_temp = Column(Float, default=4.0, nullable=False)
    temp_safe = Column(Boolean, default=True, nullable=False)
    humidity = Column(Float, default=90.0, nullable=False)
    shelf_life_days_total = Column(Integer, default=14, nullable=False)
    shelf_life_remaining_days = Column(Integer, default=11, nullable=False)
    grade = Column(String, default="A", nullable=False)  # A, B, C
    quality_score = Column(Integer, default=94, nullable=False)
    cargo_health_score = Column(Integer, default=96, nullable=False)
    status = Column(
        String,
        default="Pre-Cooling",
        nullable=False,
        index=True,
    )  # Pre-Cooling, In-Transit, Stored, Dispatched, Delivered
    allocated_hub = Column(String, nullable=True)
    assigned_vehicle = Column(String, nullable=True)
    mandi_rate_per_kg = Column(Float, default=140.0, nullable=False)
    escrow_secured_amount = Column(Float, default=0.0, nullable=False)
    payout_status = Column(String, default="Escrow Secured", nullable=False)  # Escrow Secured, Processing, Paid
    payout_amount = Column(String, nullable=True)
    subsidy_eligible = Column(String, default="PMKSY Capital Subsidy Eligible", nullable=False)
    sensor_verification_score = Column(Integer, default=99, nullable=False)
    qr_payload = Column(String, nullable=True)
    eta = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<CropBatch id={self.id!r} crop={self.crop!r} farmer={self.farmer_name!r}>"

"""CropBatch database service for farmer consignments and agricultural hubs."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.CropBatch import CropBatch as CropBatchModel
from schemas.CropBatch import CropBatchCreate, CropBatchUpdate


def list_crop_batches(db: Session, status: Optional[str] = None) -> List[CropBatchModel]:
    """Retrieve registered agricultural crop batches."""
    stmt = select(CropBatchModel)
    if status:
        stmt = stmt.where(CropBatchModel.status == status)
    stmt = stmt.order_by(CropBatchModel.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_crop_batch(db: Session, batch_id: str) -> Optional[CropBatchModel]:
    """Get batch by ID."""
    stmt = select(CropBatchModel).where(CropBatchModel.id == batch_id)
    return db.execute(stmt).scalar_one_or_none()


def create_crop_batch(db: Session, batch_in: CropBatchCreate) -> CropBatchModel:
    """Register a new harvest consignment batch."""
    db_batch = CropBatchModel(**batch_in.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def update_crop_batch(db: Session, batch_id: str, update_in: CropBatchUpdate) -> Optional[CropBatchModel]:
    """Update status, temperature readings, or escrow payout."""
    batch = get_crop_batch(db, batch_id)
    if not batch:
        return None
    for field, val in update_in.model_dump(exclude_unset=True).items():
        setattr(batch, field, val)
    db.commit()
    db.refresh(batch)
    return batch

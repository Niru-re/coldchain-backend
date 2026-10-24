"""Shipment and Telematics database service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from models.Shipment import Shipment as ShipmentModel
from models.Position import Position as PositionModel
from models.Event import Event as EventModel
from schemas.Shipment import ShipmentCreate, ShipmentUpdate, PositionPingCreate


def list_shipments(
    db: Session,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ShipmentModel]:
    """Retrieve filtered and paginated shipments."""
    stmt = select(ShipmentModel)
    if status:
        stmt = stmt.where(ShipmentModel.status == status)
    if category:
        stmt = stmt.where(ShipmentModel.category == category)
    if search:
        search_fmt = f"%{search}%"
        stmt = stmt.where(
            or_(
                ShipmentModel.tracking_number.ilike(search_fmt),
                ShipmentModel.commodity.ilike(search_fmt),
                ShipmentModel.origin.ilike(search_fmt),
                ShipmentModel.destination.ilike(search_fmt),
            )
        )
    stmt = stmt.order_by(ShipmentModel.created_at.desc()).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def count_shipments(
    db: Session,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    """Count total matching shipments."""
    stmt = select(func.count(ShipmentModel.id))
    if status:
        stmt = stmt.where(ShipmentModel.status == status)
    if category:
        stmt = stmt.where(ShipmentModel.category == category)
    if search:
        search_fmt = f"%{search}%"
        stmt = stmt.where(
            or_(
                ShipmentModel.tracking_number.ilike(search_fmt),
                ShipmentModel.commodity.ilike(search_fmt),
                ShipmentModel.origin.ilike(search_fmt),
                ShipmentModel.destination.ilike(search_fmt),
            )
        )
    return db.execute(stmt).scalar() or 0


def get_shipment(db: Session, shipment_id: str) -> Optional[ShipmentModel]:
    """Get single shipment by ID or tracking number."""
    stmt = select(ShipmentModel).where(
        or_(
            ShipmentModel.id == shipment_id,
            ShipmentModel.tracking_number == shipment_id,
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def create_shipment(db: Session, shipment_in: ShipmentCreate) -> ShipmentModel:
    """Create a new cold-chain shipment consignment."""
    db_shipment = ShipmentModel(**shipment_in.model_dump())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment


def update_shipment(db: Session, shipment_id: str, update_in: ShipmentUpdate) -> Optional[ShipmentModel]:
    """Update shipment status, location, sensor values, or waypoints."""
    shipment = get_shipment(db, shipment_id)
    if not shipment:
        return None

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(shipment, field, val)

    db.commit()
    db.refresh(shipment)
    return shipment


def record_position_ping(db: Session, ping_in: PositionPingCreate) -> PositionModel:
    """Record GPS / sensor breadcrumb and update current shipment location."""
    pos = PositionModel(**ping_in.model_dump())
    db.add(pos)

    # If shipment_id is provided, update shipment's current coordinates/temperature
    if ping_in.shipment_id:
        shipment = get_shipment(db, ping_in.shipment_id)
        if shipment:
            shipment.current_location = f"Lat: {ping_in.latitude:.4f}, Lon: {ping_in.longitude:.4f}"
            if ping_in.temperature is not None:
                shipment.temperature = ping_in.temperature
            if ping_in.humidity is not None:
                shipment.humidity = ping_in.humidity
            if ping_in.battery_level is not None:
                shipment.battery_level = ping_in.battery_level
            if ping_in.door_status is not None:
                shipment.door_status = ping_in.door_status
            if ping_in.reefer_status is not None:
                shipment.reefer_status = ping_in.reefer_status

    db.commit()
    db.refresh(pos)
    return pos


def get_shipment_positions(db: Session, shipment_id: str, limit: int = 50) -> List[PositionModel]:
    """Get chronological GPS trail for a shipment."""
    stmt = (
        select(PositionModel)
        .where(PositionModel.shipment_id == shipment_id)
        .order_by(PositionModel.recorded_at.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def get_shipment_events(db: Session, shipment_id: str) -> List[EventModel]:
    """Get audit events and milestone checkpoints for a shipment."""
    stmt = (
        select(EventModel)
        .where(EventModel.shipment_id == shipment_id)
        .order_by(EventModel.occurred_at.asc())
    )
    return db.execute(stmt).scalars().all()

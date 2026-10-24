"""Fleet, Truck, Driver, and Assignment database service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.Truck import Truck as TruckModel
from models.Driver import Driver as DriverModel
from models.Assignment import Assignment as AssignmentModel
from schemas.Fleet import TruckCreate, TruckUpdate, DriverCreate, DriverUpdate, AssignmentCreate


def list_trucks(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[TruckModel]:
    """Retrieve trucks with optional status filter."""
    stmt = select(TruckModel)
    if status:
        stmt = stmt.where(TruckModel.status == status)
    stmt = stmt.order_by(TruckModel.id.asc()).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def get_truck(db: Session, truck_id: str) -> Optional[TruckModel]:
    """Get single truck by ID or plate number."""
    stmt = select(TruckModel).where(
        (TruckModel.id == truck_id) | (TruckModel.plate_number == truck_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def create_truck(db: Session, truck_in: TruckCreate) -> TruckModel:
    """Register a new vehicle in the reefer fleet."""
    db_truck = TruckModel(**truck_in.model_dump())
    db.add(db_truck)
    db.commit()
    db.refresh(db_truck)
    return db_truck


def update_truck(db: Session, truck_id: str, update_in: TruckUpdate) -> Optional[TruckModel]:
    """Update truck telemetry, driver assignment, or operating status."""
    truck = get_truck(db, truck_id)
    if not truck:
        return None

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(truck, field, val)

    db.commit()
    db.refresh(truck)
    return truck


def list_drivers(db: Session, status: Optional[str] = None) -> List[DriverModel]:
    """Retrieve all fleet drivers."""
    stmt = select(DriverModel)
    if status:
        stmt = stmt.where(DriverModel.status == status)
    stmt = stmt.order_by(DriverModel.name.asc())
    return db.execute(stmt).scalars().all()


def get_driver(db: Session, driver_id: int) -> Optional[DriverModel]:
    """Get driver by ID."""
    stmt = select(DriverModel).where(DriverModel.id == driver_id)
    return db.execute(stmt).scalar_one_or_none()


def create_driver(db: Session, driver_in: DriverCreate) -> DriverModel:
    """Add a new verified driver."""
    db_driver = DriverModel(**driver_in.model_dump())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def create_assignment(db: Session, assignment_in: AssignmentCreate) -> AssignmentModel:
    """Create a dispatch assignment linking shipment, vehicle, and driver."""
    db_assignment = AssignmentModel(**assignment_in.model_dump())
    db.add(db_assignment)

    # Update truck status
    if assignment_in.truck_id:
        truck = get_truck(db, assignment_in.truck_id)
        if truck:
            truck.status = "En Route"

    # Update driver status
    if assignment_in.driver_id:
        driver = get_driver(db, assignment_in.driver_id)
        if driver:
            driver.status = "On Trip"

    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def list_assignments(db: Session, status: Optional[str] = None) -> List[AssignmentModel]:
    """List dispatch assignments."""
    stmt = select(AssignmentModel)
    if status:
        stmt = stmt.where(AssignmentModel.status == status)
    stmt = stmt.order_by(AssignmentModel.assigned_at.desc())
    return db.execute(stmt).scalars().all()

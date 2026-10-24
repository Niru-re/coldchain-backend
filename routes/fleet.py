"""Fleet and Driver management routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.Fleet import (
    TruckResponse,
    TruckCreate,
    TruckUpdate,
    DriverResponse,
    DriverCreate,
    AssignmentResponse,
    AssignmentCreate,
)
from services import fleet as fleet_service

router = APIRouter(prefix="/fleet", tags=["Fleet Management"])


@router.get("/trucks", response_model=List[TruckResponse])
def get_trucks(
    status: Optional[str] = Query(None, description="Filter by status (En Route, Docking, Standby, Maintenance Required)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Retrieve reefer trucks with optional status filter."""
    return fleet_service.list_trucks(db=db, status=status, skip=skip, limit=limit)


@router.get("/trucks/{truck_id}", response_model=TruckResponse)
def get_truck_by_id(truck_id: str, db: Session = Depends(get_db)):
    """Retrieve single truck by ID or license plate."""
    truck = fleet_service.get_truck(db=db, truck_id=truck_id)
    if not truck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Truck with ID or plate '{truck_id}' not found",
        )
    return truck


@router.post("/trucks", response_model=TruckResponse, status_code=status.HTTP_201_CREATED)
def create_truck(truck_in: TruckCreate, db: Session = Depends(get_db)):
    """Register a new vehicle in the reefer fleet."""
    existing = fleet_service.get_truck(db=db, truck_id=truck_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Truck with ID '{truck_in.id}' already exists",
        )
    return fleet_service.create_truck(db=db, truck_in=truck_in)


@router.patch("/trucks/{truck_id}", response_model=TruckResponse)
def update_truck(truck_id: str, truck_in: TruckUpdate, db: Session = Depends(get_db)):
    """Update truck status, driver, or telematics."""
    truck = fleet_service.update_truck(db=db, truck_id=truck_id, update_in=truck_in)
    if not truck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Truck with ID '{truck_id}' not found",
        )
    return truck


@router.get("/drivers", response_model=List[DriverResponse])
def get_drivers(
    status: Optional[str] = Query(None, description="Filter drivers by status (Available, On Trip, Off Duty)"),
    db: Session = Depends(get_db),
):
    """Retrieve all verified fleet drivers."""
    return fleet_service.list_drivers(db=db, status=status)


@router.get("/drivers/{driver_id}", response_model=DriverResponse)
def get_driver_by_id(driver_id: int, db: Session = Depends(get_db)):
    """Retrieve single driver by ID."""
    driver = fleet_service.get_driver(db=db, driver_id=driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with ID {driver_id} not found",
        )
    return driver


@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(driver_in: DriverCreate, db: Session = Depends(get_db)):
    """Add a new verified driver to the fleet roster."""
    return fleet_service.create_driver(db=db, driver_in=driver_in)


@router.get("/assignments", response_model=List[AssignmentResponse])
def get_assignments(
    status: Optional[str] = Query(None, description="Filter assignments by status"),
    db: Session = Depends(get_db),
):
    """List dispatch assignments."""
    return fleet_service.list_assignments(db=db, status=status)


@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment_in: AssignmentCreate, db: Session = Depends(get_db)):
    """Assign a vehicle and driver to an active shipment."""
    return fleet_service.create_assignment(db=db, assignment_in=assignment_in)

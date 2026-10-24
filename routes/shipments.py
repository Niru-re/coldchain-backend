"""Shipments and Tracking API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from routes.auth import get_current_active_user
from models.User import User as UserModel
from schemas.Shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentResponse,
    ShipmentListResponse,
    PositionPingCreate,
)
from services.shipment import (
    list_shipments,
    count_shipments,
    get_shipment,
    create_shipment,
    update_shipment,
    record_position_ping,
    get_shipment_positions,
    get_shipment_events,
)

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("", response_model=ShipmentListResponse)
def get_shipments(
    status: Optional[str] = Query(None, description="Filter by status (e.g., 'In Transit', 'Critical Alert')"),
    category: Optional[str] = Query(None, description="Filter by cargo category"),
    search: Optional[str] = Query(None, description="Search tracking number, commodity, or route"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieve filtered and paginated list of cold-chain shipments."""
    items = list_shipments(db, status=status, category=category, search=search, skip=skip, limit=limit)
    total = count_shipments(db, status=status, category=category, search=search)
    return ShipmentListResponse(total=total, items=items)


@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment_by_id(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    """Get single shipment details by ID or tracking number."""
    shipment = get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment '{shipment_id}' not found",
        )
    return shipment


@router.post("", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_new_shipment(
    shipment_in: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Create a new cold-chain consignment (requires authentication)."""
    # Check for duplicate tracking number or ID
    existing = get_shipment(db, shipment_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shipment with ID '{shipment_in.id}' already exists",
        )
    return create_shipment(db, shipment_in)


@router.patch("/{shipment_id}", response_model=ShipmentResponse)
def update_shipment_details(
    shipment_id: str,
    update_in: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    """Update shipment status, telemetry, or assigned vehicles."""
    updated = update_shipment(db, shipment_id, update_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment '{shipment_id}' not found",
        )
    return updated


@router.post("/telematics/ping", status_code=status.HTTP_201_CREATED)
def ingest_telematics_ping(
    ping_in: PositionPingCreate,
    db: Session = Depends(get_db),
):
    """Ingest a live GPS breadcrumb and sensor telemetry ping."""
    pos = record_position_ping(db, ping_in)
    return {"status": "recorded", "id": pos.id, "recorded_at": pos.recorded_at}


@router.get("/{shipment_id}/positions")
def get_positions(
    shipment_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieve GPS breadcrumb and temperature tracking history."""
    return get_shipment_positions(db, shipment_id, limit=limit)


@router.get("/{shipment_id}/events")
def get_events(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve tracking milestones and incident audit events for a shipment."""
    return get_shipment_events(db, shipment_id)

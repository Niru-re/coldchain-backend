"""Warehouse facilities and chambers routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.Warehouse import (
    WarehouseNodeResponse,
    WarehouseNodeCreate,
    WarehouseChamberResponse,
    WarehouseChamberCreate,
)
from services import warehouse as warehouse_service

router = APIRouter(prefix="/warehouses", tags=["Warehouse Nodes"])


@router.get("/nodes", response_model=List[WarehouseNodeResponse])
def get_warehouse_nodes(db: Session = Depends(get_db)):
    """Retrieve all cold storage terminal nodes."""
    return warehouse_service.list_warehouse_nodes(db=db)


@router.get("/nodes/{node_id}", response_model=WarehouseNodeResponse)
def get_warehouse_node_by_id(node_id: str, db: Session = Depends(get_db)):
    """Retrieve single warehouse facility details."""
    node = warehouse_service.get_warehouse_node(db=db, node_id=node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse facility '{node_id}' not found",
        )
    return node


@router.post("/nodes", response_model=WarehouseNodeResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse_node(node_in: WarehouseNodeCreate, db: Session = Depends(get_db)):
    """Register a new cold storage warehouse facility."""
    existing = warehouse_service.get_warehouse_node(db=db, node_id=node_in.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Warehouse facility '{node_in.id}' already exists",
        )
    return warehouse_service.create_warehouse_node(db=db, node_in=node_in)


@router.get("/chambers", response_model=List[WarehouseChamberResponse])
def get_warehouse_chambers(
    warehouse_id: Optional[str] = Query(None, description="Filter chambers by warehouse facility ID"),
    db: Session = Depends(get_db),
):
    """List temperature-controlled storage chambers."""
    return warehouse_service.list_warehouse_chambers(db=db, warehouse_id=warehouse_id)


@router.post("/chambers", response_model=WarehouseChamberResponse, status_code=status.HTTP_201_CREATED)
def create_warehouse_chamber(chamber_in: WarehouseChamberCreate, db: Session = Depends(get_db)):
    """Register a new cold storage chamber."""
    return warehouse_service.create_warehouse_chamber(db=db, chamber_in=chamber_in)

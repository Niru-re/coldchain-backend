"""Warehouse nodes and chambers database service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.Warehouse import WarehouseNode as NodeModel, WarehouseChamber as ChamberModel
from schemas.Warehouse import WarehouseNodeCreate, WarehouseChamberCreate


def list_warehouse_nodes(db: Session) -> List[NodeModel]:
    """Retrieve all regional cold-chain warehouse nodes."""
    stmt = select(NodeModel).order_by(NodeModel.name.asc())
    return db.execute(stmt).scalars().all()


def get_warehouse_node(db: Session, node_id: str) -> Optional[NodeModel]:
    """Get single warehouse node by ID."""
    stmt = select(NodeModel).where(NodeModel.id == node_id)
    return db.execute(stmt).scalar_one_or_none()


def create_warehouse_node(db: Session, node_in: WarehouseNodeCreate) -> NodeModel:
    """Create a new cold storage terminal entry."""
    db_node = NodeModel(**node_in.model_dump())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


def list_warehouse_chambers(db: Session, warehouse_id: Optional[str] = None) -> List[ChamberModel]:
    """List cold storage chambers, optionally filtered by facility."""
    stmt = select(ChamberModel)
    if warehouse_id:
        stmt = stmt.where(ChamberModel.warehouse_id == warehouse_id)
    stmt = stmt.order_by(ChamberModel.chamber_id.asc())
    return db.execute(stmt).scalars().all()


def create_warehouse_chamber(db: Session, chamber_in: WarehouseChamberCreate) -> ChamberModel:
    """Register a new temperature-controlled chamber."""
    db_chamber = ChamberModel(**chamber_in.model_dump())
    db.add(db_chamber)
    db.commit()
    db.refresh(db_chamber)
    return db_chamber

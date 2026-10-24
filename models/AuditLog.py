"""Audit log model for compliance, security, and traceability."""

from sqlalchemy import Column, Integer, String, DateTime, JSON, func, ForeignKey
from db.base import Base


class AuditLog(Base):
    """Immutable audit trail for actions performed within ColdChain 360."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # Login, Create Shipment, Acknowledge Alert, Update Role, Dispatch Rescue
    entity_type = Column(String, nullable=False, index=True)  # User, Shipment, Alert, Truck, Chamber
    entity_id = Column(String, nullable=True, index=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r} entity={self.entity_type!r}>"

from sqlalchemy import Column, ForeignKey, DateTime, Enum, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base
from .enums import AuditAction, AuditEntityType

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    action = Column(Enum(AuditAction), nullable=False)
    entity_type = Column(Enum(AuditEntityType), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    details = Column(JSON, nullable=True)  # Additional context about the action

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="audit_logs")

from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import relationship
from ..database.core import Base
from .enums import OrgRole, TranslationStatus

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    role = Column(Enum(OrgRole), nullable=False, default=OrgRole.MEMBER)
    # status = Column(Enum(TranslationStatus), nullable=True, default=TranslationStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organizations")

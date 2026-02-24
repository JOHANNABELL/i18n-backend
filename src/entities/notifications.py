from sqlalchemy import Column, ForeignKey, DateTime, Enum, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from ..database.core import Base
from .enums import NotificationType

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    type = Column(Enum(NotificationType), default=NotificationType.INFO)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
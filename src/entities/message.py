from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base
from .enums import MessageStatus

class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("file_id", "key", name="uq_file_message_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    file_id = Column(UUID(as_uuid=True), ForeignKey("translation_files.id", ondelete="CASCADE"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    key = Column(String, nullable=False)
    value = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    file = relationship("TranslationFile", back_populates="messages")
    creator = relationship("User", foreign_keys=[created_by])

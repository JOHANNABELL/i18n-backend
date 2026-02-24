from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base

class TranslationVersion(Base):
    __tablename__ = "translation_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    file_id = Column(UUID(as_uuid=True), ForeignKey("translation_files.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    version_number = Column(Integer, nullable=False)
    snapshot_json = Column(JSON, nullable=False)  # Snapshot of all messages at this version

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    file = relationship("TranslationFile", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])

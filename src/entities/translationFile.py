from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base

class TranslationFile(Base):
    __tablename__ = "translation_files"
    __table_args__ = (
        UniqueConstraint("project_id", "language_code", name="uq_project_language"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    language_code = Column(String, nullable=False)
    language_name = Column(String, nullable=False)
    current_version = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="files")
    messages = relationship("Message", back_populates="file", cascade="all, delete-orphan")
    versions = relationship("TranslationVersion", back_populates="file", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])

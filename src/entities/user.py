from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..database.core import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)

    organizations = relationship("OrganizationMember", back_populates="user")
    project_members = relationship("ProjectMember", back_populates="user")
    created_files = relationship("TranslationFile", foreign_keys="TranslationFile.created_by", back_populates="creator")
    created_versions = relationship("TranslationVersion", foreign_keys="TranslationVersion.created_by", back_populates="creator")

    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}')>"

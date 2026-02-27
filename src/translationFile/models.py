from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime


class TranslationFileCreate(BaseModel):
    """DTO for creating a translation file"""
    language_code: str = Field(..., min_length=2, max_length=10, description="Language code (e.g., 'fr', 'es')")
    language_name: str = Field(..., min_length=1, max_length=255, description="Language name (e.g., 'French')")


class TranslationFileUpdate(BaseModel):
    """DTO for updating a translation file"""
    language_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Language name")


class TranslationFileResponse(BaseModel):
    """Response model for translation files"""
    id: UUID
    project_id: UUID
    created_by: Optional[UUID]
    language_code: str
    language_name: str
    current_version: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class MessageExport(BaseModel):
    """Export model for a single message"""
    key: str
    value: Optional[str]
    status: str
    comment: Optional[str]


class ExportResponse(BaseModel):
    """Response model for file export"""
    language_code: str
    language_name: str
    version: int
    messages: List[MessageExport] = Field(description="List of messages in file")
    exported_at: datetime


class ImportPayload(BaseModel):
    """Payload for importing translation messages"""
    messages: Dict[str, str] = Field(..., description="Dictionary of message keys to values")

from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class TranslationFileCreate(BaseModel):
    language_code: str = Field(..., min_length=2, max_length=10, description="Language code (e.g., 'fr', 'es')")
    language_name: str = Field(..., min_length=1, max_length=255, description="Language name (e.g., 'French')")


class TranslationFileResponse(BaseModel):
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


class ImportPayload(BaseModel):
    messages: Dict[str, str] = Field(..., description="Dictionary of message keys to values")


class ExportResponse(BaseModel):
    language_code: str
    language_name: str
    version: int
    messages: Dict[str, str] = Field(description="Dictionary of approved messages")
    exported_at: datetime

class TranslationFileUpdate(BaseModel):
    language_code: str
    language_name : str
    messages: Dict[str, str] = Field(description="Dictionary of approved messages")
     
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    source_language: str = Field(..., min_length=2, max_length=10, description="Source language code (e.g., 'en')")
    target_languages: List[str] = Field(..., min_items=1, description="List of target language codes")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    source_language: Optional[str] = Field(None, min_length=2, max_length=10, description="Source language code")
    target_languages: Optional[List[str]] = Field(None, min_items=1, description="List of target language codes")


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    organization_id: UUID
    created_by: Optional[UUID]
    source_language: str
    target_languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

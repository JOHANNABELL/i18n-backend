from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    """DTO for creating a project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    source_language: str = Field(..., min_length=2, max_length=10, description="Source language code (e.g., 'en')")
    target_languages: List[str] = Field(..., min_items=1, description="List of target language codes")


class ProjectUpdate(BaseModel):
    """DTO for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    source_language: Optional[str] = Field(None, min_length=2, max_length=10, description="Source language code")
    target_languages: Optional[List[str]] = Field(None, min_items=1, description="List of target language codes")


class ProjectMemberInfo(BaseModel):
    """Member info for projects"""
    id: UUID
    name: str
    email: EmailStr


class ProjectResponse(BaseModel):
    """Basic response model for projects"""
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


class ProjectDetailedResponse(BaseModel):
    """Detailed response with members for projects"""
    id: UUID
    name: str
    description: Optional[str]
    organization_id: UUID
    created_by: Optional[UUID]
    source_language: str
    target_languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    members: List[ProjectMemberInfo] = []  # List of users from project_member

    class Config:
        from_attributes = True


class ProjectStatsResponse(BaseModel):
    """Response model for project statistics"""
    project_id: UUID
    name: str
    files: int
    total_messages: int
    members: int

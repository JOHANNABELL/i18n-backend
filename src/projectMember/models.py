from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..entities.enums import ProjectRole


class ProjectMemberCreate(BaseModel):
    """DTO for adding a member to a project"""
    user_id: UUID = Field(..., description="User ID to add to project")
    role: ProjectRole = Field(..., description="Role in project (LEAD, TRANSLATOR, REVIEWER)")


class ProjectMemberUpdate(BaseModel):
    """DTO for updating a project member's role"""
    role: ProjectRole = Field(..., description="New role in project (LEAD, TRANSLATOR, REVIEWER)")


class ProjectMemberResponse(BaseModel):
    """Response model for project members"""
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

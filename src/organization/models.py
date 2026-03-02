from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class OrganizationCreate(BaseModel):
    """DTO for creating an organization"""
    name: str
    description: str


class OrganizationUpdate(BaseModel):
    """DTO for updating an organization"""
    name: str | None = None
    description: str | None = None


class MemberInfo(BaseModel):
    """Nested member info for organizations and projects"""
    id: UUID
    name: str
    email: EmailStr


class OrganizationResponse(BaseModel):
    """Basic response model for organizations"""
    id: UUID
    name: str
    description: str
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


class OrganizationDetailedResponse(BaseModel):
    """Detailed response with members for organizations"""
    id: UUID
    name: str
    description: str
    created_at: datetime
    created_by: UUID
    members: List[MemberInfo] = []  # List of users from organization_member

    class Config:
        from_attributes = True

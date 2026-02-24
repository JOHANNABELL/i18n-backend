from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
import logging


class OrganizationCreate(BaseModel):
    name: str
    description: str


class OrganizationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True  # permet de convertir SQLAlchemy → Pydantic
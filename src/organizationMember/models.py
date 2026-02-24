from enum import Enum
from uuid import UUID 
from datetime import datetime 
import logging
from ..entities.enums import OrgRole
from pydantic import BaseModel

class OrganizationMemberCreate(BaseModel):
    user_id : UUID
    organization_id : UUID
    role : str

class OrganizationMemberUpdate(BaseModel):
    organization_id : UUID
    user_id : UUID
    new_role :  str

class OrganizationMemberResponse(BaseModel):
    organization_id: UUID
    user_id : UUID
    org_name: str
    user_name : str
    user_email: str
    role : Enum

    class Config:
        from_attributes = True

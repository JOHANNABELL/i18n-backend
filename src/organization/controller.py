from typing import List
from fastapi import APIRouter, status
from uuid import UUID
from ..database.core import DbSession
from . import models 
from . import service
from ..auth.service import CurrentUser, get_current_user




router = APIRouter(
    prefix="/organizations",
    tags = ["Organizations"]
)


#CREATE 
@router.post("/", response_model=models.OrganizationResponse)
def create_organization(
    org_data: models.OrganizationCreate,
    db:DbSession,
    current_user: CurrentUser
):
    return service.create_organization(db, org_data, current_user.get_uuid())




# DELETE
@router.delete("/{org_id}")
def delete_organization(org_id: UUID, db: DbSession):
    service.delete_organization(db, org_id)
    return {"message": "Organization deleted successfully"}


# UPDATE
@router.put("/{org_id}", response_model=models.OrganizationResponse)
def update_organization(
    org_id: UUID,
    update_data: models.OrganizationUpdate,
    db: DbSession
):
    return service.update_organization(db, org_id, update_data)


# READ by ID
@router.get("/{org_id}", response_model=models.OrganizationResponse)
def get_organization(org_id: UUID, db: DbSession):
    return service.get_organization_by_id(db, org_id)


# READ by name
@router.get("/by-name/{name}", response_model=models.OrganizationResponse)
def get_by_name(name: str, db: DbSession):
    return service.get_organization_by_name(db, name)


# READ by user
@router.get("/user/{user_id}", response_model=List[models.OrganizationResponse])
def get_by_user(user_id: UUID, db: DbSession):
    return service.get_organizations_by_user(db, user_id)

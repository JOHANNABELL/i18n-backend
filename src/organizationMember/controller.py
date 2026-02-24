
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Query
from ..database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser
from ..entities.enums import OrgRole
router = APIRouter(
    prefix="/org_members",
    tags = ["Organization Members"]
)
# , response_model= models.OrganizationMemberCreate
# CREATE 
@router.post("/")
def create_organization(
    member_data: models.OrganizationMemberCreate,
    db: DbSession, 
    current_user: CurrentUser
):
    
   return service.create_organization_member(db, member_data)


# Delete 

@router.delete("/delete/org/{org_id}")
def delete_org_members(org_id:UUID, db:DbSession):
    service.delete_by_organization(db, org_id)
    return {"message : Organization deleted successfully"}

@router.delete("/delete/user/{user_id}")
def delete_member_by_id(user_id:UUID, db:DbSession):
    service.delete_by_user(db, user_id)
    return {"message" : "Members deleted  successfully"}

@router.delete("/{user_id}/{org_id}")
def delete_member_from_org(user_id:UUID,org_id:UUID, db:DbSession):
    service.delete_member(db, org_id, user_id)
    return {"message" : "Members deleted  successfully"}

# READ member
#  response_model=List[models.OrganizationMemberResponse]
@router.get("/by-user/")
def read_members(
    # data : models.OrganizationMemberCreate,
    db:DbSession,
    user_id: Optional[UUID] = Query(None),
    organization_id: Optional[UUID] = Query(None),
    role: Optional[OrgRole] = Query(None)
    ):
    return service.get_members(
        db,
        user_id=user_id,
        organization_id=organization_id,
        role=role
    )
# Update member

@router.put("/")
def update_org_members(
    db: DbSession, 
    update_data:models.OrganizationMemberUpdate):
    
    return service.update_member_role(db, update_data)


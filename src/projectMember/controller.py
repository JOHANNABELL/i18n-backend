from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from ..database.core import DbSession
from ..auth.service import CurrentUser
from ..exceptions import (
    MemberAlreadyExistsException,
    MemberNotFoundException,
    CannotRemoveLastLeadException,
    UnauthorizedException,
)
from .service import ProjectMemberService
from .models import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from typing import List

router = APIRouter(prefix="/projects/{project_id}/members", tags=["project-members"])


@router.post("", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: UUID,
    member: ProjectMemberCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Add a member to a project"""
    try:
        result = ProjectMemberService.add_member(db, project_id, current_user.id, current_user.id, member)
        return result
    except MemberAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to add member")


@router.get("", response_model=List[ProjectMemberResponse])
def list_members(
    project_id: UUID,
    db: DbSession,
):
    """List all members in a project"""
    try:
        return ProjectMemberService.list_members(db, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list members")


@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_member(
    project_id: UUID,
    member_id: UUID,
    db: DbSession,
):
    """Get a project member"""
    try:
        member = ProjectMemberService.get_member(db, member_id)
        if member.project_id != project_id:
            raise HTTPException(status_code=404, detail="Member not found in this project")
        return member
    except MemberNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch member")


@router.patch("/{member_id}", response_model=ProjectMemberResponse)
def update_member(
    project_id: UUID,
    member_id: UUID,
    member_update: ProjectMemberUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a member's role"""
    try:
        result = ProjectMemberService.update_member_role(
            db, member_id, project_id, current_user.id, member_update
        )
        return result
    except MemberNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update member")


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: UUID,
    member_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Remove a member from a project"""
    try:
        ProjectMemberService.remove_member(db, member_id, project_id, current_user.id)
    except MemberNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CannotRemoveLastLeadException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to remove member")

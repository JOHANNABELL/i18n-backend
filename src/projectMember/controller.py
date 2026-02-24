from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.core import get_db
from .service import ProjectMemberService
from .models import ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse
from typing import List

router = APIRouter(prefix="/projects/{project_id}/members", tags=["project-members"])


def get_current_user_id() -> UUID:
    """Get current user from token - placeholder"""
    return UUID("00000000-0000-0000-0000-000000000000")


@router.post("", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: UUID,
    member: ProjectMemberCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Add a member to a project"""
    try:
        return ProjectMemberService.add_member(db, project_id, user_id, member.user_id, member)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ProjectMemberResponse])
def list_members(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """List all members in a project"""
    return ProjectMemberService.list_members(db, project_id)


@router.get("/{member_id}", response_model=ProjectMemberResponse)
def get_member(
    project_id: UUID,
    member_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a project member"""
    try:
        member = ProjectMemberService.get_member(db, member_id)
        if not member or member.project_id != project_id:
            raise HTTPException(status_code=404, detail="Member not found")
        return member
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{member_id}", response_model=ProjectMemberResponse)
def update_member(
    project_id: UUID,
    member_id: UUID,
    member_update: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update a member's role"""
    try:
        return ProjectMemberService.update_member_role(
            db, member_id, project_id, user_id, member_update
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: UUID,
    member_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Remove a member from a project"""
    try:
        ProjectMemberService.remove_member(db, member_id, project_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

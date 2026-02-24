from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.core import get_db
from .service import ProjectService
from .models import ProjectCreate, ProjectUpdate, ProjectResponse
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])


# TODO: Add authentication dependency - for now using user_id as path param
def get_current_user_id() -> UUID:
    """Get current user from token - placeholder"""
    return UUID("00000000-0000-0000-0000-000000000000")


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    organization_id: UUID,
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new project"""
    try:
        return ProjectService.create_project(db, organization_id, user_id, project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    """Get a project by ID"""
    try:
        return ProjectService.get_project(db, project_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    organization_id: UUID,
    db: Session = Depends(get_db),
):
    """List all projects in an organization"""
    return ProjectService.list_projects(db, organization_id)


@router.get("/user/projects", response_model=List[ProjectResponse])
def list_user_projects(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """List all projects for current user"""
    return ProjectService.list_user_projects(db, user_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update a project"""
    try:
        return ProjectService.update_project(db, project_id, user_id, project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a project"""
    try:
        ProjectService.delete_project(db, project_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/stats")
def get_project_stats(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """Get project statistics"""
    try:
        return ProjectService.get_project_stats(db, project_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

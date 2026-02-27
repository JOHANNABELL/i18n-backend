from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.core import DbSession
from ..auth.service import CurrentUser
from ..exceptions import (
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
    UnauthorizedException,
)
from .service import ProjectService
from .models import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectStatsResponse
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    organization_id: UUID,
    project: ProjectCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new project"""
    try:
        result = ProjectService.create_project(db, organization_id, current_user.id, project)
        return result
    except ProjectAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create project")


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, db: DbSession):
    """Get a project by ID"""
    try:
        return ProjectService.get_project(db, project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch project")


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    organization_id: UUID,
    db: DbSession,
):
    """List all projects in an organization"""
    try:
        return ProjectService.list_projects(db, organization_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list projects")


@router.get("/user/projects", response_model=List[ProjectResponse])
def list_user_projects(
    db: DbSession,
    current_user: CurrentUser,
):
    """List all projects for current user"""
    try:
        return ProjectService.list_user_projects(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list user projects")


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a project"""
    try:
        result = ProjectService.update_project(db, project_id, current_user.id, project)
        return result
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update project")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a project"""
    try:
        ProjectService.delete_project(db, project_id, current_user.id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete project")


@router.get("/{project_id}/stats", response_model=ProjectStatsResponse)
def get_project_stats(
    project_id: UUID,
    db: DbSession,
):
    """Get project statistics"""
    try:
        return ProjectService.get_project_stats(db, project_id)
    except ProjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch project statistics")

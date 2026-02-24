from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.core import get_db
from .service import TranslationFileService
from .models import TranslationFileCreate, TranslationFileUpdate, TranslationFileResponse
from typing import List

router = APIRouter(prefix="/projects/{project_id}/files", tags=["translation-files"])


def get_current_user_id() -> UUID:
    """Get current user from token - placeholder"""
    return UUID("00000000-0000-0000-0000-000000000000")


@router.post("", response_model=TranslationFileResponse, status_code=status.HTTP_201_CREATED)
def create_file(
    project_id: UUID,
    file: TranslationFileCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new translation file"""
    try:
        return TranslationFileService.create_file(db, project_id, user_id, file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[TranslationFileResponse])
def list_files(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """List all translation files in a project"""
    return TranslationFileService.list_files(db, project_id)


@router.get("/{file_id}", response_model=TranslationFileResponse)
def get_file(
    project_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a translation file"""
    try:
        file = TranslationFileService.get_file(db, file_id)
        if file.project_id != project_id:
            raise HTTPException(status_code=404, detail="File not found in this project")
        return file
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{file_id}", response_model=TranslationFileResponse)
def update_file(
    project_id: UUID,
    file_id: UUID,
    file_update: TranslationFileUpdate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update a translation file"""
    try:
        return TranslationFileService.update_file(db, file_id, user_id, project_id, file_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    project_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a translation file"""
    try:
        TranslationFileService.delete_file(db, file_id, user_id, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{file_id}/export")
def export_file(
    project_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
):
    """Export a translation file as JSON"""
    try:
        return TranslationFileService.export_file(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{file_id}/versions")
def get_version_history(
    project_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
):
    """Get version history of a translation file"""
    try:
        return TranslationFileService.get_version_history(db, file_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

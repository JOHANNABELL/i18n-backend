from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from ..database.core import DbSession
from ..auth.service import CurrentUser
from ..exceptions import (
    FileAlreadyExistsException,
    FileNotFoundException,
    LanguageNotAllowedException,
    UnauthorizedException,
)
from .service import TranslationFileService
from .models import TranslationFileCreate, TranslationFileUpdate, TranslationFileResponse, ExportResponse
from typing import List

router = APIRouter(prefix="/projects/{project_id}/files", tags=["translation-files"])


@router.post("", response_model=TranslationFileResponse, status_code=status.HTTP_201_CREATED)
def create_file(
    project_id: UUID,
    file: TranslationFileCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new translation file"""
    try:
        result = TranslationFileService.create_file(db, project_id, current_user.id, file)
        return result
    except FileAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LanguageNotAllowedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create translation file")


@router.get("", response_model=List[TranslationFileResponse])
def list_files(
    project_id: UUID,
    db: DbSession,
):
    """List all translation files in a project"""
    try:
        return TranslationFileService.list_files(db, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list translation files")


@router.get("/{file_id}", response_model=TranslationFileResponse)
def get_file(
    project_id: UUID,
    file_id: UUID,
    db: DbSession,
):
    """Get a translation file"""
    try:
        file = TranslationFileService.get_file(db, file_id)
        if file.project_id != project_id:
            raise HTTPException(status_code=404, detail="File not found in this project")
        return file
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch translation file")


@router.patch("/{file_id}", response_model=TranslationFileResponse)
def update_file(
    project_id: UUID,
    file_id: UUID,
    file_update: TranslationFileUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a translation file"""
    try:
        result = TranslationFileService.update_file(db, file_id, current_user.id, project_id, file_update)
        return result
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update translation file")


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    project_id: UUID,
    file_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a translation file"""
    try:
        TranslationFileService.delete_file(db, file_id, current_user.id, project_id)
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete translation file")


@router.get("/{file_id}/export", response_model=ExportResponse)
def export_file(
    project_id: UUID,
    file_id: UUID,
    db: DbSession,
):
    """Export a translation file as JSON"""
    try:
        return TranslationFileService.export_file(db, file_id)
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export translation file")


@router.get("/{file_id}/versions")
def get_version_history(
    project_id: UUID,
    file_id: UUID,
    db: DbSession,
):
    """Get version history of a translation file"""
    try:
        return TranslationFileService.get_version_history(db, file_id)
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch version history")

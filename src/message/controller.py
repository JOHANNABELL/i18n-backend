from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.core import get_db
from .service import MessageService
from .models import MessageCreate, MessageUpdate, MessageResponse
from typing import List, Optional

router = APIRouter(prefix="/files/{file_id}/messages", tags=["messages"])


def get_current_user_id() -> UUID:
    """Get current user from token - placeholder"""
    return UUID("00000000-0000-0000-0000-000000000000")


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    file_id: UUID,
    message: MessageCreate,
    project_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new message"""
    try:
        return MessageService.create_message(db, file_id, user_id, message, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[MessageResponse])
def list_messages(
    file_id: UUID,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all messages in a file"""
    try:
        return MessageService.list_messages(db, file_id, status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    file_id: UUID,
    message_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single message"""
    try:
        message = MessageService.get_message(db, message_id)
        if message.file_id != file_id:
            raise HTTPException(status_code=404, detail="Message not found in this file")
        return message
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{message_id}", response_model=MessageResponse)
def update_message(
    file_id: UUID,
    message_id: UUID,
    message_update: MessageUpdate,
    project_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update a message value"""
    try:
        return MessageService.update_message(db, message_id, user_id, message_update, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{message_id}/approve", response_model=MessageResponse)
def approve_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Approve a pending message"""
    try:
        return MessageService.approve_message(db, message_id, user_id, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{message_id}/reject", response_model=MessageResponse)
def reject_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Reject a pending message"""
    try:
        return MessageService.reject_message(db, message_id, user_id, project_id, reason)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a message"""
    try:
        MessageService.delete_message(db, message_id, user_id, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

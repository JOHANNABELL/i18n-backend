from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from ..database.core import DbSession
from ..auth.service import CurrentUser
from ..exceptions import (
    KeyAlreadyExistsException,
    MessageNotFoundException,
    InvalidStatusTransitionException,
    UnauthorizedException,
    FileNotFoundException,
)
from .service import MessageService
from .models import MessageCreate, MessageUpdate, MessageResponse
from typing import List, Optional

router = APIRouter(prefix="/files/{file_id}/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    file_id: UUID,
    message: MessageCreate,
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Create a new message"""
    try:
        result = MessageService.create_message(db, file_id, current_user.id, message, project_id)
        return result
    except KeyAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to create message")


@router.get("", response_model=List[MessageResponse])
def list_messages(
    file_id: UUID,
    status: Optional[str] = None,
    db: DbSession = None,
):
    """List all messages in a file"""
    try:
        return MessageService.list_messages(db, file_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list messages")


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    file_id: UUID,
    message_id: UUID,
    db: DbSession,
):
    """Get a single message"""
    try:
        message = MessageService.get_message(db, message_id)
        if message.file_id != file_id:
            raise HTTPException(status_code=404, detail="Message not found in this file")
        return message
    except MessageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch message")


@router.patch("/{message_id}", response_model=MessageResponse)
def update_message(
    file_id: UUID,
    message_id: UUID,
    message_update: MessageUpdate,
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Update a message value"""
    try:
        result = MessageService.update_message(db, message_id, current_user.id, message_update, project_id)
        return result
    except MessageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update message")


@router.post("/{message_id}/approve", response_model=MessageResponse)
def approve_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Approve a pending message"""
    try:
        result = MessageService.approve_message(db, message_id, current_user.id, project_id)
        return result
    except MessageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStatusTransitionException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to approve message")


@router.post("/{message_id}/reject", response_model=MessageResponse)
def reject_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    reason: Optional[str] = None,
    db: DbSession = None,
    current_user: CurrentUser = None,
):
    """Reject a pending message"""
    try:
        result = MessageService.reject_message(db, message_id, current_user.id, project_id, reason)
        return result
    except MessageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStatusTransitionException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to reject message")


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    file_id: UUID,
    message_id: UUID,
    project_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
):
    """Delete a message"""
    try:
        MessageService.delete_message(db, message_id, current_user.id, project_id)
    except MessageNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete message")

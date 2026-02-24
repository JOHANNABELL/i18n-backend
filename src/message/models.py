from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..entities.enums import MessageStatus


class MessageCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=500, description="Translation key")
    value: str = Field(..., min_length=0, max_length=5000, description="Translated value")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment or note")


class MessageUpdate(BaseModel):
    value: Optional[str] = Field(None, min_length=0, max_length=5000, description="Updated translation value")
    comment: Optional[str] = Field(None, max_length=1000, description="Updated comment")


class MessageStatusUpdate(BaseModel):
    status: MessageStatus = Field(..., description="New status (APPROVED or REJECTED)")
    reason: Optional[str] = Field(None, max_length=1000, description="Reason for approval/rejection")


class MessageResponse(BaseModel):
    id: UUID
    file_id: UUID
    key: str
    value: Optional[str]
    comment: Optional[str]
    status: MessageStatus
    created_by: Optional[UUID]
    reviewed_by: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

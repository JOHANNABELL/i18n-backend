from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from src.entities.todo import Priority


class TodoBase(BaseModel):
    """Base model for todos"""
    description: str = Field(..., min_length=1, max_length=1000, description="Todo description")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    priority: Priority = Field(default=Priority.Medium, description="Priority level")


class TodoCreate(TodoBase):
    """DTO for creating a todo"""
    pass


class TodoUpdate(BaseModel):
    """DTO for updating a todo"""
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="Todo description")
    due_date: Optional[datetime] = Field(None, description="Due date for the todo")
    priority: Optional[Priority] = Field(None, description="Priority level")


class TodoResponse(TodoBase):
    """Response model for todos"""
    id: UUID
    is_completed: bool
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

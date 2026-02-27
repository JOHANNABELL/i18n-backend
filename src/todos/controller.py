from fastapi import APIRouter, status, HTTPException
from typing import List
from uuid import UUID

from ..database.core import DbSession
from ..exceptions import TodoCreationError, TodoNotFoundError
from . import models
from .service import TodoService
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


@router.post("/", response_model=models.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(db: DbSession, todo: models.TodoCreate, current_user: CurrentUser):
    """Create a new todo"""
    try:
        return TodoService.create_todo(current_user.id, db, todo)
    except TodoCreationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create todo")


@router.get("/", response_model=List[models.TodoResponse])
def get_todos(db: DbSession, current_user: CurrentUser):
    """Get all todos for current user"""
    try:
        return TodoService.get_todos(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch todos")


@router.get("/{todo_id}", response_model=models.TodoResponse)
def get_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    """Get a specific todo by ID"""
    try:
        return TodoService.get_todo_by_id(current_user.id, db, todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch todo")


@router.patch("/{todo_id}", response_model=models.TodoResponse)
def update_todo(db: DbSession, todo_id: UUID, todo_update: models.TodoUpdate, current_user: CurrentUser):
    """Update a todo"""
    try:
        return TodoService.update_todo(current_user.id, db, todo_id, todo_update)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to update todo")


@router.put("/{todo_id}/complete", response_model=models.TodoResponse)
def complete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    """Mark a todo as completed"""
    try:
        return TodoService.complete_todo(current_user.id, db, todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to complete todo")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db: DbSession, todo_id: UUID, current_user: CurrentUser):
    """Delete a todo"""
    try:
        TodoService.delete_todo(current_user.id, db, todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to delete todo")

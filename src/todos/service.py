from datetime import datetime, timezone
from uuid import UUID
import logging
from sqlalchemy.orm import Session
from . import models
from src.entities.todo import Todo
from src.exceptions import TodoCreationError, TodoNotFoundError


logger = logging.getLogger(__name__)


class TodoService:
    """Service for managing todos"""

    @staticmethod
    def create_todo(user_id: UUID, db: Session, todo: models.TodoCreate) -> Todo:
        """Create a new todo for a user"""
        logger.debug(f"Creating todo for user {user_id}")
        
        try:
            new_todo = Todo(
                user_id=user_id,
                description=todo.description,
                due_date=todo.due_date,
                priority=todo.priority,
            )
            db.add(new_todo)
            db.commit()
            db.refresh(new_todo)
            logger.info(f"Todo created with id: {new_todo.id}")
            return new_todo
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create todo for user {user_id}: {str(e)}")
            raise TodoCreationError(str(e))

    @staticmethod
    def get_todos(user_id: UUID, db: Session) -> list:
        """Get all todos for a user"""
        logger.debug(f"Fetching todos for user {user_id}")
        
        todos = db.query(Todo).filter(Todo.user_id == user_id).all()
        logger.info(f"Retrieved {len(todos)} todos for user {user_id}")
        return todos

    @staticmethod
    def get_todo_by_id(user_id: UUID, db: Session, todo_id: UUID) -> Todo:
        """Get a specific todo by ID"""
        logger.debug(f"Fetching todo {todo_id} for user {user_id}")
        
        todo = db.query(Todo).filter(
            Todo.id == todo_id,
            Todo.user_id == user_id
        ).first()
        if not todo:
            logger.warning(f"Todo {todo_id} not found for user {user_id}")
            raise TodoNotFoundError(todo_id)
        return todo

    @staticmethod
    def update_todo(user_id: UUID, db: Session, todo_id: UUID, todo_update: models.TodoUpdate) -> Todo:
        """Update a todo"""
        logger.debug(f"Updating todo {todo_id} for user {user_id}")
        
        todo = TodoService.get_todo_by_id(user_id, db, todo_id)
        
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        db.commit()
        db.refresh(todo)
        logger.info(f"Todo {todo_id} updated")
        return todo

    @staticmethod
    def complete_todo(user_id: UUID, db: Session, todo_id: UUID) -> Todo:
        """Mark a todo as completed"""
        logger.debug(f"Completing todo {todo_id} for user {user_id}")
        
        todo = TodoService.get_todo_by_id(user_id, db, todo_id)
        
        if todo.is_completed:
            logger.debug(f"Todo {todo_id} is already completed")
            return todo
        
        todo.is_completed = True
        todo.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(todo)
        logger.info(f"Todo {todo_id} marked as completed")
        return todo

    @staticmethod
    def delete_todo(user_id: UUID, db: Session, todo_id: UUID) -> None:
        """Delete a todo"""
        logger.debug(f"Deleting todo {todo_id} for user {user_id}")
        
        todo = TodoService.get_todo_by_id(user_id, db, todo_id)
        db.delete(todo)
        db.commit()
        logger.info(f"Todo {todo_id} deleted")

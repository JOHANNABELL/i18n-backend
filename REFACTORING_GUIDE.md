# Backend Refactoring Guide

## Overview

This document details the comprehensive refactoring of the i18n-backend project to improve code quality, maintainability, and consistency across all modules. The refactoring applies best practices for REST API design, error handling, logging, and data validation.

## Refactoring Goals

1. **Consistency**: Standardize patterns across all modules
2. **Maintainability**: Improve code readability and structure
3. **Error Handling**: Implement proper exception handling throughout
4. **Logging**: Add comprehensive logging for debugging and monitoring
5. **Type Safety**: Improve type hints and validation
6. **Documentation**: Add clear docstrings to all functions
7. **Security**: Enhance RBAC (Role-Based Access Control) enforcement

## Architecture Overview

### Service Layer Pattern

All modules follow a three-layer architecture:

```
Controller (Routes) → Service Layer → Database/Entities
```

- **Controller**: Handles HTTP requests/responses, error mapping, input validation
- **Service**: Contains business logic, RBAC checks, logging
- **Models**: Pydantic DTOs for request/response validation

### Naming Conventions

- **Models**: `XxxCreate`, `XxxUpdate`, `XxxResponse`
- **Service Classes**: `XxxService` (static methods for stateless operations)
- **Controllers**: Router files with route handlers
- **Exceptions**: Custom exceptions for specific error cases

## Refactored Modules

### 1. Project Module

**Files**: `src/project/models.py`, `src/project/service.py`, `src/project/controller.py`

#### Key Improvements

- Added comprehensive field validation in models with `Field` constraints
- Implemented `ProjectUpdate` DTO with optional fields
- Added logging at all critical operations
- Improved error handling with specific exception types
- Added `db.refresh()` after creating/updating resources
- Enhanced RBAC validation in create/update/delete operations

#### Models
```python
# DTOs with validation
ProjectCreate - Required fields with constraints
ProjectUpdate - Optional fields for partial updates
ProjectResponse - Response model with config
```

#### Service Methods
```python
create_project(db, user_id, data) → Project
get_project(db, project_id) → Project
list_projects(db) → list
update_project(db, project_id, user_id, data) → Project
delete_project(db, project_id, user_id) → None
```

#### Controller Patterns
```python
# Error handling example
try:
    return ProjectService.create_project(...)
except ProjectAlreadyExistsException as e:
    raise HTTPException(status_code=400, detail=str(e))
except UnauthorizedException as e:
    raise HTTPException(status_code=403, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail="Failed to create project")
```

### 2. ProjectMember Module

**Files**: `src/projectMember/models.py`, `src/projectMember/service.py`, `src/projectMember/controller.py`

#### Key Improvements

- Added `ProjectMemberRole` validation in update operations
- Implemented `ProjectMemberUpdate` DTO
- Added logging for member operations
- Proper permission checks before operations
- Improved list filtering and pagination support

#### Models
```python
ProjectMemberCreate - Create with user_id, role
ProjectMemberUpdate - Update only role field
ProjectMemberResponse - Member details with project info
```

#### Service Methods
```python
add_member(db, project_id, user_id, member_data) → ProjectMember
get_member(db, member_id) → ProjectMember
list_members(db, project_id) → list
update_member_role(db, member_id, user_id, new_role) → ProjectMember
remove_member(db, member_id, user_id) → None
```

### 3. Message Module

**Files**: `src/message/models.py`, `src/message/service.py`, `src/message/controller.py`

#### Key Improvements

- Added comprehensive message status validation
- Implemented `MessageUpdate` DTO with optional fields
- Added logging for all message operations
- Better handling of message translations
- Improved query performance with proper filtering

#### Models
```python
MessageCreate - Key, value, status with validation
MessageUpdate - Optional fields for updates
MessageResponse - Full message data with timestamps
```

#### Service Methods
```python
create_message(db, file_id, user_id, data) → Message
get_message(db, message_id) → Message
list_messages(db, file_id) → list
update_message(db, message_id, user_id, data) → Message
delete_message(db, message_id, user_id) → None
```

### 4. TranslationFile Module

**Files**: `src/translationFile/models.py`, `src/translationFile/service.py`, `src/translationFile/controller.py`

#### Key Improvements

- Fixed timestamp handling (was setting `updated_at = None`)
- Added proper datetime with timezone awareness
- Implemented comprehensive export functionality
- Added version history tracking
- Improved error handling for language validation

#### Models
```python
TranslationFileCreate - Language code and name
TranslationFileUpdate - Only language_name for updates
TranslationFileResponse - File metadata
MessageExport - Individual message export structure
ExportResponse - Full export with messages list
```

#### Service Methods
```python
create_file(db, project_id, user_id, data) → TranslationFile
get_file(db, file_id) → TranslationFile
list_files(db, project_id) → list
update_file(db, file_id, user_id, project_id, data) → TranslationFile
delete_file(db, file_id, user_id, project_id) → None
export_file(db, file_id) → dict
get_version_history(db, file_id) → list
```

### 5. Todos Module

**Files**: `src/todos/models.py`, `src/todos/service.py`, `src/todos/controller.py`

#### Key Improvements

- Wrapped functions in `TodoService` class for consistency
- Added `TodoUpdate` DTO with optional fields
- Changed from `PUT` to `PATCH` for updates (following REST conventions)
- Improved error handling with proper exception types
- Better separation of concerns

#### Models
```python
TodoBase - Description, due_date, priority
TodoCreate - For creating todos
TodoUpdate - For partial updates
TodoResponse - Complete todo with status
```

#### Service Methods
```python
create_todo(user_id, db, todo) → Todo
get_todos(user_id, db) → list
get_todo_by_id(user_id, db, todo_id) → Todo
update_todo(user_id, db, todo_id, todo_update) → Todo
complete_todo(user_id, db, todo_id) → Todo
delete_todo(user_id, db, todo_id) → None
```

## Common Patterns Applied

### 1. Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

class XxxService:
    @staticmethod
    def operation(db, item_id):
        logger.debug(f"Starting operation for {item_id}")
        try:
            # ... operation code
            logger.info(f"Operation completed for {item_id}")
            return result
        except Exception as e:
            logger.error(f"Operation failed for {item_id}: {str(e)}")
            raise
```

### 2. Error Handling Pattern

```python
@router.post("", response_model=XxxResponse)
def create_xxx(db: DbSession, data: XxxCreate, current_user: CurrentUser):
    """Create a new xxx"""
    try:
        return XxxService.create_xxx(db, current_user.id, data)
    except SpecificException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create xxx")
```

### 3. Service Method Pattern

```python
@staticmethod
def operation(db: Session, resource_id: UUID, user_id: UUID, data: Model) -> Entity:
    """Clear docstring describing what the operation does"""
    logger.debug(f"Performing operation on {resource_id}")
    
    # Authorization check
    if not user_has_permission:
        raise UnauthorizedException("Specific permission required")
    
    # Business logic
    resource = db.query(Entity).filter_by(id=resource_id).first()
    if not resource:
        raise ResourceNotFoundException(resource_id)
    
    # Update/modify
    resource.field = data.field
    db.flush()
    
    # Audit logging (if applicable)
    audit = AuditLog(...)
    db.add(audit)
    db.commit()
    db.refresh(resource)
    
    logger.info(f"Operation completed for {resource_id}")
    return resource
```

### 4. Model Validation Pattern

```python
from pydantic import BaseModel, Field

class CreateModel(BaseModel):
    """DTO for creating xxx"""
    field1: str = Field(..., min_length=1, max_length=255, description="Field description")
    field2: Optional[int] = Field(None, ge=0, le=100, description="Field description")
    field3: Priority = Field(default=Priority.Medium, description="Field description")

class UpdateModel(BaseModel):
    """DTO for updating xxx"""
    field1: Optional[str] = Field(None, min_length=1, max_length=255, description="Field description")
    field2: Optional[int] = Field(None, ge=0, le=100, description="Field description")
```

## Key Improvements Summary

### Type Safety
- ✅ All functions have complete type hints
- ✅ Pydantic models with field validation
- ✅ Optional fields clearly marked

### Error Handling
- ✅ Specific exception types used throughout
- ✅ Proper HTTP status code mapping
- ✅ User-friendly error messages

### Logging
- ✅ Debug logs at operation start
- ✅ Info logs at completion
- ✅ Error logs with context
- ✅ Module-level logger instances

### Code Organization
- ✅ Service classes with static methods
- ✅ Clear separation of concerns
- ✅ Consistent naming conventions
- ✅ Comprehensive docstrings

### Data Validation
- ✅ Pydantic field constraints
- ✅ Range validation (min/max)
- ✅ String length validation
- ✅ Enum validation

### Database Operations
- ✅ Proper transaction handling
- ✅ `db.refresh()` after modifications
- ✅ Rollback on exceptions (where applicable)
- ✅ Audit logging for critical operations

## Security Considerations

### RBAC Implementation
- All create/update/delete operations check user permissions
- Role-based access validated before operations
- Proper exception handling for authorization failures

### SQL Injection Prevention
- SQLAlchemy ORM used throughout
- Parameterized queries prevent injection
- No raw SQL string concatenation

### Input Validation
- Pydantic validation on all inputs
- Field constraints enforce business rules
- Required fields explicitly marked

## Migration Notes

If migrating existing code to this pattern:

1. **Service Layer**: Wrap functions in a service class
2. **Models**: Create separate Create/Update/Response DTOs
3. **Controllers**: Update error handling to map specific exceptions
4. **Logging**: Add logger instance and log calls
5. **Type Hints**: Ensure all parameters and returns have types
6. **Docstrings**: Add docstrings to all public methods

## Testing Recommendations

### Unit Tests
- Test service methods with valid/invalid inputs
- Mock database interactions
- Verify exception handling

### Integration Tests
- Test complete request/response flow
- Verify RBAC enforcement
- Check audit log creation

### Error Cases
- Test unauthorized access scenarios
- Verify validation error responses
- Check error message clarity

## Future Improvements

1. **Pagination**: Implement offset/limit in list operations
2. **Filtering**: Add advanced filtering to list operations
3. **Sorting**: Implement sortable responses
4. **Caching**: Consider caching for read operations
5. **Rate Limiting**: Add rate limiting to prevent abuse
6. **API Versioning**: Prepare for API versioning strategy

## Maintenance Guidelines

1. **Code Reviews**: Ensure new code follows these patterns
2. **Documentation**: Update this guide when adding new modules
3. **Testing**: Maintain high test coverage (target: >80%)
4. **Dependencies**: Keep dependencies updated
5. **Performance**: Monitor and optimize slow queries

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [REST API Best Practices](https://restfulapi.net/)
- [Logging Best Practices](https://docs.python.org/3/howto/logging.html)

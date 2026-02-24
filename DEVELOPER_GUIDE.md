# i18n-Backend Developer Guide

## Quick Start

### 1. Database is Ready
The Neon PostgreSQL database has been initialized with all required tables, enums, and constraints via `scripts/create_schema.sql`.

### 2. API Endpoints Overview

#### Projects
```bash
# Create project (auth required)
POST /projects
Body: {
  "organization_id": "uuid",
  "name": "My Project",
  "description": "...",
  "source_language": "en",
  "target_languages": ["es", "fr"]
}

# Get project stats
GET /projects/{project_id}/stats
Response: {
  "project_id": "uuid",
  "name": "My Project",
  "files": 2,
  "total_messages": 150,
  "members": 5
}
```

#### Translation Files
```bash
# Create file for Spanish
POST /projects/{project_id}/files
Body: {
  "language_code": "es",
  "language_name": "Spanish"
}

# Export as JSON for translation
GET /projects/{project_id}/files/{file_id}/export
Response: {
  "language_code": "es",
  "language_name": "Spanish",
  "messages": [
    {
      "key": "greeting",
      "value": "Hola",
      "status": "APPROVED",
      "comment": "..."
    }
  ]
}

# Get version history
GET /projects/{project_id}/files/{file_id}/versions
```

#### Messages
```bash
# Create message
POST /files/{file_id}/messages
Body: {
  "key": "greeting",
  "value": "Hola",
  "comment": "..."
}

# List all messages (with optional status filter)
GET /files/{file_id}/messages?status=PENDING
GET /files/{file_id}/messages?status=APPROVED

# Approve message (LEAD/ADMIN only)
POST /files/{file_id}/messages/{message_id}/approve

# Reject message (LEAD/ADMIN only)
POST /files/{file_id}/messages/{message_id}/reject
Body: {
  "reason": "Incorrect translation"
}

# Update message (atomic workflow - creates version)
PATCH /files/{file_id}/messages/{message_id}
Body: {
  "value": "New translation",
  "comment": "Updated comment"
}
```

#### Project Members
```bash
# Add member to project (ADMIN only)
POST /projects/{project_id}/members
Body: {
  "user_id": "uuid",
  "role": "EDITOR"  # VIEWER, EDITOR, LEAD, ADMIN
}

# List all members
GET /projects/{project_id}/members

# Update member role (ADMIN only)
PATCH /projects/{project_id}/members/{member_id}
Body: {
  "role": "LEAD"
}

# Remove member (ADMIN only)
DELETE /projects/{project_id}/members/{member_id}
```

## Understanding the Architecture

### Service Layer Pattern
All business logic is in service classes (`*Service`):

```python
# Example: Message service
class MessageService:
    @staticmethod
    def create_message(db: Session, file_id: UUID, user_id: UUID, data: MessageCreate, project_id: UUID) -> Message:
        # 1. RBAC check - verify user is EDITOR or higher
        # 2. Validation - check message key doesn't exist
        # 3. Create message
        # 4. Audit log
        # 5. Commit
```

**Key principle**: Service methods are static and take `Session` as first param for dependency injection.

### RBAC Implementation

**Role Hierarchy**: VIEWER < EDITOR < LEAD < ADMIN

**Where RBAC is checked**:
- Service layer (all methods)
- Exceptions raised with 403 Forbidden
- Never in controller

**Example role checks**:
```python
# VIEWER: Read-only
member = db.query(ProjectMember).filter_by(project_id=project_id, user_id=user_id).first()
if member.role == ProjectRole.VIEWER:
    raise UnauthorizedException()

# EDITOR+: Can create/update
if member.role == ProjectRole.VIEWER:
    raise UnauthorizedException()

# LEAD/ADMIN: Can approve
if member.role not in [ProjectRole.LEAD, ProjectRole.ADMIN]:
    raise UnauthorizedException()

# ADMIN only
if member.role != ProjectRole.ADMIN:
    raise UnauthorizedException()
```

### Atomic Message Update Workflow

When a message is updated, these operations happen in a **single transaction**:

```
1. Update message.value
   ↓
2. Create AuditLog (UPDATE action)
   ↓
3. Increment TranslationFile.current_version
   ↓
4. Create TranslationVersion (snapshot of all messages)
   ↓
5. Create AuditLog (VERSION action)
   ↓
6. COMMIT
   
If ANY step fails → ROLLBACK (entire transaction)
```

This ensures consistency: every message change has corresponding audit trail and version snapshot.

**Implementation**:
```python
def update_message(db, message_id, user_id, data, project_id):
    try:
        message.value = data.value
        db.flush()
        
        # Create audit
        audit = AuditLog(...)
        db.add(audit)
        db.flush()
        
        # Increment version
        file.current_version += 1
        db.flush()
        
        # Create snapshot
        snapshot = {...}
        version = TranslationVersion(..., snapshot_json=snapshot)
        db.add(version)
        db.flush()
        
        # Audit version
        version_audit = AuditLog(...)
        db.add(version_audit)
        
        db.commit()  # All succeed or all fail
    except Exception:
        db.rollback()
        raise
```

## Adding New Features

### Adding a New Service Method

1. **Add to service class** (`src/{module}/service.py`):
```python
@staticmethod
def new_operation(db: Session, resource_id: UUID, user_id: UUID, data: SomeModel) -> SomeEntity:
    # 1. Fetch resource
    resource = db.query(SomeEntity).filter_by(id=resource_id).first()
    if not resource:
        raise SomeNotFoundException()
    
    # 2. RBAC check
    member = db.query(ProjectMember).filter_by(project_id=project_id, user_id=user_id).first()
    if member.role != ProjectRole.ADMIN:
        raise UnauthorizedException()
    
    # 3. Perform operation
    resource.field = data.field
    db.flush()
    
    # 4. Audit
    audit = AuditLog(user_id=user_id, project_id=project_id, action=AuditAction.UPDATE, ...)
    db.add(audit)
    db.commit()
    
    return resource
```

2. **Add to controller** (`src/{module}/controller.py`):
```python
@router.post("/{resource_id}/new_action", response_model=SomeResponse)
def new_action(
    resource_id: UUID,
    data: SomeRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    try:
        return SomeService.new_operation(db, resource_id, user_id, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

3. **Add tests** (`tests/test_{feature}.py`):
```python
def test_new_operation(db: Session):
    # Setup
    resource = create_test_resource(db)
    
    # Execute
    result = SomeService.new_operation(db, resource.id, user_id, data)
    
    # Assert
    assert result.field == expected_value
```

## Common Patterns

### Error Handling
```python
# In service
if condition_not_met:
    raise SpecificException("message")

# In controller
try:
    return service_method()
except SpecificException as e:
    raise HTTPException(status_code=403, detail=str(e))
```

### RBAC Check Pattern
```python
member = db.query(ProjectMember).filter_by(
    project_id=project_id, user_id=user_id
).first()
if not member or member.role not in allowed_roles:
    raise UnauthorizedException("message")
```

### Audit Log Pattern
```python
audit = AuditLog(
    user_id=user_id,
    project_id=project_id,
    action=AuditAction.CREATE,
    entity_type=AuditEntityType.MESSAGE,
    entity_id=message.id,
    details={"key": message.key, ...}
)
db.add(audit)
```

### Transaction Pattern
```python
try:
    # Operations
    resource.field = value
    db.flush()
    
    audit = AuditLog(...)
    db.add(audit)
    db.flush()
    
    db.commit()
except Exception:
    db.rollback()
    raise
```

## Database Schema Reference

### Key Tables
- **projects** - Project configuration
- **project_members** - Team members with roles
- **translation_files** - Language-specific files
- **messages** - Individual translations with status
- **translation_versions** - Version history with snapshots
- **audit_logs** - All changes for compliance

### Key Constraints
- `uq_org_project_name` - One project name per org
- `uq_project_user` - User can't have duplicate roles in project
- `uq_project_language` - One file per language per project
- `uq_file_message_key` - One key per message file

## Debugging

### Enable SQL Logging
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Check Audit Logs
```python
audits = db.query(AuditLog).filter_by(
    project_id=project_id,
    entity_type=AuditEntityType.MESSAGE
).order_by(AuditLog.created_at.desc()).all()
```

### Verify Version Snapshots
```python
version = db.query(TranslationVersion).filter_by(
    file_id=file_id,
    version_number=n
).first()
print(version.snapshot_json)  # All messages at this version
```

## Performance Notes

- Use `db.flush()` for partial commits to check constraints
- Version snapshots are stored as JSON for flexibility
- Index on `project_id`, `file_id`, `user_id` for query performance
- Audit logs can grow large - consider archiving

## Testing Checklist

When adding features:
- [ ] Write service method test
- [ ] Test happy path
- [ ] Test error paths (missing resource, RBAC denied, etc.)
- [ ] Test atomicity (if multi-step operation)
- [ ] Test audit trail created
- [ ] Write controller integration test

---
**Last Updated**: Phase 7 Complete - All services, controllers, and tests implemented.

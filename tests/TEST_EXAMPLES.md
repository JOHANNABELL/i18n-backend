# Test Examples for i18n-Backend

This document provides practical examples of how to write tests for the i18n-Backend using the available fixtures and patterns.

## Table of Contents

1. [Basic Database Tests](#basic-database-tests)
2. [API Endpoint Tests](#api-endpoint-tests)
3. [RBAC Tests](#rbac-tests)
4. [Atomic Workflow Tests](#atomic-workflow-tests)
5. [Error Handling Tests](#error-handling-tests)
6. [Factory Pattern Tests](#factory-pattern-tests)

---

## Basic Database Tests

### Test 1: Create and Query a User

```python
"""
tests/examples/test_user_basic.py
Basic database operations with a single user
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.entities.user import User
from src.auth.service import get_password_hash


@pytest.mark.unit
def test_user_creation(db_session: Session):
    """Test that a user can be created and retrieved"""
    # Arrange
    user_data = {
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password_hash": get_password_hash("secure_password"),
    }
    
    # Act
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    
    # Assert
    assert user.id is not None
    assert user.email == "john@example.com"
    assert user.created_at is not None


@pytest.mark.unit
def test_user_retrieval(test_user, db_session: Session):
    """Test retrieving a user from database"""
    # Act
    retrieved_user = db_session.query(User).filter_by(id=test_user.id).first()
    
    # Assert
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


@pytest.mark.unit
def test_user_update(test_user, db_session: Session):
    """Test updating user attributes"""
    # Arrange
    original_name = test_user.first_name
    
    # Act
    test_user.first_name = "Updated"
    db_session.commit()
    
    # Assert
    updated_user = db_session.query(User).filter_by(id=test_user.id).first()
    assert updated_user.first_name == "Updated"
    assert updated_user.first_name != original_name
```

### Test 2: Multiple Users Interaction

```python
@pytest.mark.unit
def test_multiple_users(test_users: dict, db_session: Session):
    """Test interactions between multiple users"""
    alice = test_users["alice"]
    bob = test_users["bob"]
    
    # Verify both users exist
    assert alice.email == "alice@example.com"
    assert bob.email == "bob@example.com"
    
    # Verify they're different
    assert alice.id != bob.id
    
    # Verify count
    all_users = db_session.query(User).all()
    assert len(all_users) >= 2
```

---

## API Endpoint Tests

### Test 3: GET Endpoint

```python
"""
tests/examples/test_api_get.py
Testing GET endpoints
"""
import pytest


@pytest.mark.integration
def test_list_users_endpoint(client, auth_headers):
    """Test GET /users endpoint returns users"""
    response = client.get("/users", headers=auth_headers)
    
    assert response.status_code == 200
    assert "users" in response.json()
    assert isinstance(response.json()["users"], list)


@pytest.mark.integration
def test_get_user_by_id(client, auth_headers, test_user):
    """Test GET /users/{user_id} endpoint"""
    response = client.get(f"/users/{test_user.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.integration
def test_get_nonexistent_user_returns_404(client, auth_headers):
    """Test GET returns 404 for nonexistent user"""
    from uuid import uuid4
    
    fake_id = uuid4()
    response = client.get(f"/users/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404
```

### Test 4: POST Endpoint (Create)

```python
"""
tests/examples/test_api_post.py
Testing POST endpoints for creation
"""
import pytest


@pytest.mark.integration
def test_create_user_endpoint(client):
    """Test POST /auth/ for user registration"""
    response = client.post(
        "/auth/",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["id"] is not None


@pytest.mark.integration
def test_create_duplicate_user_returns_409(client):
    """Test that creating duplicate user returns conflict"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    # First creation should succeed
    response1 = client.post("/auth/", json=user_data)
    assert response1.status_code == 201
    
    # Second creation with same email should fail
    response2 = client.post("/auth/", json=user_data)
    assert response2.status_code == 409
```

### Test 5: PATCH Endpoint (Update)

```python
"""
tests/examples/test_api_patch.py
Testing PATCH endpoints for updates
"""
import pytest


@pytest.mark.integration
def test_update_user_profile(client, auth_headers, test_user):
    """Test PATCH /users/me for profile update"""
    response = client.patch(
        "/users/me",
        headers=auth_headers,
        json={
            "first_name": "Updated",
            "last_name": "Name"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
```

### Test 6: DELETE Endpoint

```python
"""
tests/examples/test_api_delete.py
Testing DELETE endpoints
"""
import pytest


@pytest.mark.integration
def test_delete_user_resource(client, auth_headers, test_user, db_session):
    """Test DELETE endpoint removes resource"""
    resource_id = test_user.id
    
    # Verify it exists
    assert db_session.query(User).filter_by(id=resource_id).first() is not None
    
    # Delete via API
    response = client.delete(
        f"/users/{resource_id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify it's gone
    assert db_session.query(User).filter_by(id=resource_id).first() is None
```

---

## RBAC Tests

### Test 7: Role-Based Access Control

```python
"""
tests/examples/test_rbac_scenarios.py
Testing role-based access control
"""
import pytest
from uuid import uuid4
from src.entities.projectMember import ProjectMember
from src.entities.project import Project
from src.entities.enums import ProjectRole
from src.exceptions import UnauthorizedException
from src.project.service import ProjectService


@pytest.mark.rbac
def test_only_admin_can_delete_project(db_session, project_factory, test_users):
    """Verify only ADMIN can delete projects"""
    alice = test_users["alice"]
    bob = test_users["bob"]
    
    # Alice (ADMIN) creates project
    project = project_factory(creator=alice)
    
    # Add Bob as TRANSLATOR
    member = ProjectMember(
        id=uuid4(),
        project_id=project.id,
        user_id=bob.id,
        role=ProjectRole.TRANSLATOR
    )
    db_session.add(member)
    db_session.commit()
    
    # Bob cannot delete
    with pytest.raises(UnauthorizedException):
        ProjectService.delete_project(db_session, project.id, bob.id)
    
    # Alice can delete
    ProjectService.delete_project(db_session, project.id, alice.id)
    
    # Project should be deleted
    assert db_session.query(Project).filter_by(id=project.id).first() is None


@pytest.mark.rbac
def test_translator_cannot_approve_messages(db_session, message_factory, test_users):
    """Verify only REVIEWER can approve messages"""
    from src.entities.message import Message
    from src.entities.translationFile import TranslationFile
    from src.entities.enums import MessageStatus
    
    alice = test_users["alice"]
    
    # Create file and message
    file = translation_file_factory()
    message = message_factory(file=file, status=MessageStatus.PENDING)
    
    # Translator trying to approve should fail
    from src.message.service import MessageService
    with pytest.raises(UnauthorizedException):
        MessageService.approve_message(
            db_session,
            message.id,
            alice.id,  # alice is not REVIEWER
            file.project_id
        )
```

### Test 8: Hierarchical Permissions

```python
@pytest.mark.rbac
def test_permission_hierarchy(db_session, organization_factory, test_users):
    """Test that higher roles include lower permissions"""
    from src.entities.organizationMember import OrganizationMember
    from src.entities.enums import OrgRole
    from src.organization.service import OrganizationService
    
    alice = test_users["alice"]
    
    org = organization_factory(admin=alice)
    
    # ADMIN should be able to do everything
    assert OrganizationService.can_manage_members(db_session, org.id, alice.id)
    assert OrganizationService.can_view_projects(db_session, org.id, alice.id)
```

---

## Atomic Workflow Tests

### Test 9: Atomic Message Update

```python
"""
tests/examples/test_atomic_workflow.py
Testing atomic transaction behavior
"""
import pytest
from uuid import uuid4
from src.entities.message import Message
from src.entities.auditLog import AuditLog
from src.entities.translationVersion import TranslationVersion


@pytest.mark.atomic
def test_message_update_creates_version_snapshot(db_session, message_factory):
    """
    Verify that updating a message:
    1. Updates the message
    2. Creates an audit log
    3. Creates a version snapshot
    All in one atomic transaction
    """
    # Arrange
    message = message_factory(key="greeting", value="Hello")
    file_id = message.file_id
    project_id = message.translation_file.project_id
    
    # Act: Update message
    from src.message.service import MessageService
    from src.message.models import MessageUpdate
    
    update_data = MessageUpdate(value="Hola")
    updated_msg = MessageService.update_message(
        db_session,
        message.id,
        message.created_by,
        update_data,
        project_id
    )
    
    # Assert: Message updated
    assert updated_msg.value == "Hola"
    
    # Assert: Version created
    versions = db_session.query(TranslationVersion)\
        .filter_by(file_id=file_id).all()
    assert len(versions) == 1
    assert "greeting" in versions[0].snapshot_json
    
    # Assert: Audit log created
    audits = db_session.query(AuditLog)\
        .filter_by(entity_id=message.id).all()
    assert len(audits) > 0


@pytest.mark.atomic
def test_transaction_rollback_on_failure(db_session, message_factory):
    """
    Verify that if any step fails, entire transaction rolls back
    """
    message = message_factory()
    original_value = message.value
    
    # Simulate failure in workflow
    try:
        with db_session.begin():
            message.value = "new_value"
            # Simulate error
            raise Exception("Simulated error")
    except Exception:
        pass
    
    # Assert: Message should NOT be updated (rollback)
    db_session.rollback()
    refreshed = db_session.query(Message).filter_by(id=message.id).first()
    assert refreshed.value == original_value
```

---

## Error Handling Tests

### Test 10: Exception Testing

```python
"""
tests/examples/test_error_handling.py
Testing error conditions and exception handling
"""
import pytest
from uuid import uuid4
from src.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ProjectAlreadyExistsException,
    KeyAlreadyExistsException,
)
from src.project.service import ProjectService
from src.message.service import MessageService


@pytest.mark.unit
def test_project_not_found_exception():
    """Test NotFoundException for missing project"""
    with pytest.raises(NotFoundException) as exc_info:
        # Try to find non-existent project
        ProjectService.get_project_or_404(uuid4())
    
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.unit
def test_unauthorized_exception():
    """Test UnauthorizedException for permission denial"""
    with pytest.raises(UnauthorizedException) as exc_info:
        # Try operation without permission
        raise UnauthorizedException("Insufficient permissions")
    
    assert "permission" in str(exc_info.value).lower()


@pytest.mark.unit
def test_duplicate_key_exception(db_session, message_factory, translation_file_factory):
    """Test KeyAlreadyExistsException"""
    file = translation_file_factory()
    
    # Create first message
    message_factory(file=file, key="duplicate")
    
    # Try to create duplicate
    with pytest.raises(KeyAlreadyExistsException):
        message_factory(file=file, key="duplicate")


@pytest.mark.unit
def test_invalid_input_validation(client):
    """Test input validation returns 422"""
    response = client.post(
        "/auth/",
        json={
            "email": "invalid-email",  # Invalid email format
            "password": "short",
            "first_name": "Test"
            # Missing last_name which might be required
        }
    )
    
    # Should return validation error
    assert response.status_code == 422
```

---

## Factory Pattern Tests

### Test 11: Using Factories Effectively

```python
"""
tests/examples/test_factory_patterns.py
Demonstrating factory usage
"""
import pytest


@pytest.mark.unit
def test_organization_with_multiple_projects(
    organization_factory,
    project_factory,
    db_session
):
    """Test creating org with multiple projects"""
    # Create organization
    org = organization_factory(name="Multi-Project Org")
    
    # Create projects under organization
    project1 = project_factory(
        name="Project 1",
        organization=org
    )
    project2 = project_factory(
        name="Project 2",
        organization=org
    )
    
    # Verify relationship
    assert project1.organization_id == org.id
    assert project2.organization_id == org.id
    
    # Count projects
    projects = db_session.query(Project).filter_by(
        organization_id=org.id
    ).all()
    assert len(projects) == 2


@pytest.mark.unit
def test_file_with_translations(translation_file_factory, message_factory):
    """Test creating translation file with messages"""
    file = translation_file_factory(language_code="es")
    
    # Create multiple translations
    messages = [
        message_factory(file=file, key="hello", value="Hola"),
        message_factory(file=file, key="goodbye", value="Adiós"),
        message_factory(file=file, key="thanks", value="Gracias"),
    ]
    
    # Verify all messages in file
    file_messages = db_session.query(Message).filter_by(
        file_id=file.id
    ).all()
    assert len(file_messages) == 3
```

---

## Running These Examples

```bash
# Run all example tests
python scripts/run_tests.py --specific TEST_EXAMPLES

# Run only RBAC examples
pytest tests/examples/test_rbac_scenarios.py -v

# Run with coverage
python scripts/run_tests.py --coverage

# Run specific example
pytest tests/examples/test_atomic_workflow.py::test_message_update_creates_version_snapshot -v
```

---

## Best Practices Summary

✅ **Do:**
- Use fixtures to reduce boilerplate
- Test one thing per test
- Use clear, descriptive names
- Follow AAA (Arrange, Act, Assert) pattern
- Use factories for complex test data
- Test error conditions
- Mark tests appropriately (@pytest.mark.unit, etc.)

❌ **Don't:**
- Test multiple unrelated things in one test
- Create test data manually when factories exist
- Write overly complex test logic
- Skip error condition testing
- Hardcode test values that could be configurable
- Make tests dependent on each other


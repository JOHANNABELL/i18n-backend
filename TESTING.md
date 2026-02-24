# Testing Guide for i18n-Backend

Complete guide to testing the i18n-Backend FastAPI application with pytest, including fixtures, markers, and best practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Fixtures](#test-fixtures)
- [Writing Tests](#writing-tests)
- [Test Markers](#test-markers)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-watch

# Run all tests
python scripts/run_tests.py

# Run with coverage
python scripts/run_tests.py --coverage

# Run specific tests
python scripts/run_tests.py --rbac
python scripts/run_tests.py --atomic
```

---

## Setup

### 1. Install Dependencies

```bash
# Core testing dependencies
pip install pytest pytest-asyncio pytest-cov

# Optional: for better test experience
pip install pytest-watch pytest-html pytest-xdist
```

### 2. Environment Configuration

The test suite uses SQLite in-memory databases by default. For PostgreSQL-specific tests:

```bash
# Copy test environment template
cp .env.test .env.test.local

# Update .env.test.local with your test database
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/i18n_test
```

### 3. Create Test Database (PostgreSQL only)

```bash
# Connect to PostgreSQL and create test database
createdb i18n_test

# Or using psql
psql -U postgres -c "CREATE DATABASE i18n_test;"
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run all tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (faster)
pytest -n auto
```

### Using the Test Runner Script

```bash
# Run all tests
python scripts/run_tests.py

# Run with verbose output
python scripts/run_tests.py -v

# Run with coverage report
python scripts/run_tests.py --coverage

# Run unit tests only
python scripts/run_tests.py --unit

# Run integration tests only
python scripts/run_tests.py --integration

# Run RBAC tests
python scripts/run_tests.py --rbac

# Run atomic workflow tests
python scripts/run_tests.py --atomic

# Run specific test file
python scripts/run_tests.py --specific test_message_workflow

# Watch mode (re-run on file changes)
python scripts/run_tests.py --watch

# Run failed tests first
python scripts/run_tests.py --failed-first

# Generate HTML report
python scripts/run_tests.py --coverage --html
```

### Advanced pytest Commands

```bash
# Run specific test class
pytest tests/test_rbac.py::TestProjectRBAC

# Run specific test method
pytest tests/test_rbac.py::TestProjectRBAC::test_only_admin_can_update_project

# Run by marker
pytest -m rbac
pytest -m "rbac or atomic"
pytest -m "not slow"

# Run with detailed output
pytest -vv --tb=long

# Show print statements
pytest -s

# Stop after N failures
pytest --maxfail=3

# Run tests that match a keyword
pytest -k "test_message"

# Show slowest tests
pytest --durations=10
```

---

## Test Fixtures

Fixtures are reusable test components. The `conftest.py` provides:

### Database Fixtures

#### `db_session`
SQLite in-memory database for each test. Use for most tests.

```python
def test_user_creation(db_session):
    user = User(email="test@example.com", ...)
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

#### `db_session_postgres`
PostgreSQL database for PostgreSQL-specific tests.

```python
def test_postgres_feature(db_session_postgres):
    # Uses real PostgreSQL
    # Skipped if PostgreSQL not available
    pass
```

### User Fixtures

#### `test_user`
Single test user.

```python
def test_user_profile(test_user):
    assert test_user.email == "test@example.com"
    assert test_user.first_name == "Test"
```

#### `test_users`
Dictionary of multiple test users (alice, bob, carol, david).

```python
def test_multi_user_scenario(test_users):
    alice = test_users["alice"]
    bob = test_users["bob"]
    assert alice.email == "alice@example.com"
```

#### `test_token_data`
Authentication token for a test user.

```python
def test_protected_endpoint(client, test_token_data):
    headers = {"Authorization": f"Bearer {test_token_data.user_id}"}
    response = client.get("/users/me", headers=headers)
```

### API Client Fixtures

#### `client`
FastAPI TestClient with database override.

```python
def test_api_endpoint(client):
    response = client.get("/users")
    assert response.status_code == 200
```

#### `auth_headers`
Authorization headers with valid token.

```python
def test_protected_route(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
```

### Factory Fixtures

#### `organization_factory`
Create organizations with members.

```python
def test_org_creation(organization_factory):
    org = organization_factory(name="My Org")
    assert org.name == "My Org"
    assert org.members.count() == 1  # Creator is added
```

#### `project_factory`
Create projects with members.

```python
def test_project_creation(project_factory):
    org = organization_factory()
    project = project_factory(
        name="My Project",
        organization=org,
        target_languages=["es", "fr"]
    )
    assert project.name == "My Project"
```

#### `translation_file_factory`
Create translation files.

```python
def test_file_creation(translation_file_factory):
    project = project_factory()
    file = translation_file_factory(
        project=project,
        language_code="es"
    )
    assert file.language_code == "es"
```

#### `message_factory`
Create translation messages.

```python
def test_message_creation(message_factory):
    file = translation_file_factory()
    msg = message_factory(
        file=file,
        key="greeting",
        value="Hello"
    )
    assert msg.key == "greeting"
```

---

## Writing Tests

### Basic Test Structure

```python
"""
Test the user service functionality
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from src.entities.user import User
from src.exceptions import NotFoundException


class TestUserService:
    """Group related tests in a class"""
    
    def test_user_can_be_created(self, db_session):
        """Test description: what is being tested and expected"""
        # Arrange: set up test data
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        
        # Act: perform the action
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        # Assert: verify the results
        assert user.id is not None
        assert user.email == "test@example.com"
    
    def test_duplicate_email_raises_error(self, db_session):
        """Test error handling"""
        # ... test code
        pass
```

### Testing with Factories

```python
def test_project_workflow(project_factory, message_factory, db_session):
    """Test complete workflow using factories"""
    # Create project through factory
    project = project_factory(name="Translation App")
    
    # Create file through factory
    file = translation_file_factory(project=project, language_code="es")
    
    # Create messages through factory
    msg1 = message_factory(file=file, key="hello", value="Hola")
    msg2 = message_factory(file=file, key="goodbye", value="Adiós")
    
    # Verify
    assert db_session.query(Message).filter_by(file_id=file.id).count() == 2
```

### Testing RBAC

```python
@pytest.mark.rbac
def test_only_leads_can_delete_project(db_session, project_factory, test_users):
    """Verify role-based access control"""
    alice = test_users["alice"]
    bob = test_users["bob"]
    
    # Alice creates project (becomes LEAD)
    project = project_factory(creator=alice)
    
    # Bob is TRANSLATOR, cannot delete
    project_member = ProjectMember(
        project_id=project.id,
        user_id=bob.id,
        role=ProjectRole.TRANSLATOR,
    )
    db_session.add(project_member)
    db_session.commit()
    
    # Verify Bob cannot delete
    with pytest.raises(UnauthorizedException):
        ProjectService.delete_project(db_session, project.id, bob.id)
```

### Testing Atomic Workflows

```python
@pytest.mark.atomic
def test_message_update_is_atomic(db_session, message_factory):
    """Verify atomic transaction behavior"""
    msg = message_factory(key="test")
    old_value = msg.value
    
    # Update message in transaction
    with db_session.begin():
        msg.value = "new_value"
        # If anything fails after this, entire transaction rolls back
    
    # Verify atomic update
    refreshed = db_session.query(Message).filter_by(id=msg.id).first()
    assert refreshed.value == "new_value"
```

---

## Test Markers

Markers help organize and filter tests:

```python
@pytest.mark.unit
def test_service_function():
    """Unit test - tests a single function"""
    pass

@pytest.mark.integration
def test_multiple_services():
    """Integration test - tests multiple components"""
    pass

@pytest.mark.rbac
def test_authorization():
    """RBAC test - verifies role-based access control"""
    pass

@pytest.mark.atomic
def test_atomic_transaction():
    """Atomic test - verifies transaction atomicity"""
    pass

@pytest.mark.slow
def test_heavy_operation():
    """Slow test - deselect with -m "not slow" """
    pass
```

Run tests by marker:

```bash
pytest -m rbac              # Run RBAC tests
pytest -m "rbac or atomic"  # Run RBAC OR atomic tests
pytest -m "not slow"        # Run all tests except slow
```

---

## Best Practices

### 1. **Test Naming**
```python
# ✓ Good: clear, descriptive names
def test_user_cannot_delete_last_project_lead():
    pass

# ✗ Bad: vague names
def test_delete():
    pass
```

### 2. **One Assertion Focus**
```python
# ✓ Better: tests one thing per test
def test_message_value_is_updated():
    msg = message_factory()
    msg.value = "new_value"
    assert msg.value == "new_value"

# ✗ Avoid: testing multiple unrelated things
def test_message():
    msg = message_factory()
    msg.value = "new"
    assert msg.value == "new"
    assert msg.status == "PENDING"
    assert msg.created_at is not None
```

### 3. **Use Fixtures Properly**
```python
# ✓ Good: compose fixtures
def test_workflow(project_factory, message_factory):
    project = project_factory()
    msg = message_factory(project=project)
    assert msg.project_id == project.id

# ✗ Avoid: recreating test data
def test_workflow(db_session):
    project = Project(...)
    db_session.add(project)
    msg = Message(...)
    db_session.add(msg)
    # Too much boilerplate
```

### 4. **AAA Pattern: Arrange, Act, Assert**
```python
def test_user_email_update():
    # Arrange: set up test data
    user = User(email="old@example.com")
    
    # Act: perform the action
    user.email = "new@example.com"
    
    # Assert: verify results
    assert user.email == "new@example.com"
```

### 5. **Test Database Isolation**
```python
# Each test gets a fresh database
# No data pollution between tests
def test_first(db_session):
    db_session.add(User(email="test@example.com"))
    db_session.commit()

def test_second(db_session):
    # This db_session is fresh, doesn't see test_first's data
    users = db_session.query(User).all()
    assert len(users) == 0
```

### 6. **Exception Testing**
```python
import pytest
from src.exceptions import NotFoundException

def test_not_found_error():
    with pytest.raises(NotFoundException) as exc_info:
        User.get_by_id(uuid4())
    
    assert "User not found" in str(exc_info.value)
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── __init__.py
├── e2e/                        # End-to-end tests
│   ├── test_auth_endpoints.py
│   ├── test_todos_endpoints.py
│   └── test_users_endpoints.py
├── unit/                       # Unit tests (optional)
├── test_auth_service.py        # Service tests
├── test_message_workflow.py    # Atomic workflow tests
├── test_rbac.py               # RBAC tests
└── test_file_operations.py    # File operation tests
```

---

## Coverage Reports

Generate and view coverage:

```bash
# Generate coverage report
python scripts/run_tests.py --coverage

# View HTML report
open htmlcov/index.html

# View in terminal
# Coverage output shows % covered for each file
```

Coverage targets:
- Aim for 80%+ overall coverage
- Critical paths (RBAC, workflows): 95%+
- Utilities and helpers: 70%+

---

## Troubleshooting

### Issue: Tests fail due to database connection

```bash
# Solution 1: Use SQLite (default)
# Tests automatically use in-memory SQLite

# Solution 2: Check PostgreSQL connection
psql -U postgres -d i18n_test -c "SELECT 1"

# Solution 3: Update DATABASE_URL in .env.test.local
```

### Issue: Fixtures not found

```python
# Solution: Ensure conftest.py is in tests/ directory
# Pytest should auto-discover fixtures from conftest.py

# If not working:
pytest --fixtures  # List all available fixtures
```

### Issue: Tests hang or timeout

```bash
# Solution: Add timeout
pip install pytest-timeout
pytest --timeout=30  # Timeout after 30 seconds

# Or mark specific tests
@pytest.mark.timeout(10)
def test_with_timeout():
    pass
```

### Issue: Flaky tests (sometimes pass, sometimes fail)

Common causes:
- Time-dependent logic
- Race conditions
- Database state issues

Solutions:
```python
# Use mocking for time
from unittest.mock import patch

def test_with_mocked_time():
    with patch('src.utils.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 1, 1)
        # ... test code
```

### Issue: Test database grows large

```bash
# Solution: SQLite tests auto-clean (in-memory)
# PostgreSQL tests auto-drop tables after each test

# Manual cleanup for PostgreSQL:
dropdb i18n_test
createdb i18n_test
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: i18n_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: python scripts/run_tests.py --coverage
        env:
          DATABASE_URL: postgresql+psycopg2://postgres:postgres@localhost:5432/i18n_test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-sessions-in-tests)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)


# Backend Testing Setup - Complete Guide

This document summarizes all the testing infrastructure that has been set up for the i18n-Backend project.

## What Has Been Created

### 1. **Enhanced Configuration**

#### `.env.test`
- Test environment template with all necessary variables
- Includes database URL, JWT settings, and logging configuration
- Safe defaults for testing (rate limiting disabled, debug mode on)

#### `pytest.ini`
- Already configured with async support
- Proper warning suppression
- Settings for test discovery and execution

#### `requirements-test.txt`
- All testing dependencies in one place
- Includes pytest, coverage, and quality tools
- Separates test dependencies from production requirements

### 2. **Comprehensive Test Fixtures** (`tests/conftest.py`)

#### Database Fixtures
- **`db_session`**: SQLite in-memory database (fast, isolated)
- **`db_session_postgres`**: Real PostgreSQL (optional, for integration tests)

#### User Management Fixtures
- **`test_user`**: Single test user with known credentials
- **`test_users`**: Multiple users (alice, bob, carol, david) for multi-user scenarios
- **`test_token_data`**: Authentication token data

#### API Client Fixtures
- **`client`**: FastAPI TestClient with DB override
- **`auth_headers`**: Pre-authenticated headers for protected endpoints

#### Factory Fixtures (Builders for Complex Data)
- **`organization_factory`**: Create organizations with members
- **`project_factory`**: Create projects with team members
- **`translation_file_factory`**: Create translation files
- **`message_factory`**: Create translation messages

### 3. **Test Runner Script** (`scripts/run_tests.py`)

Convenient command-line interface for running tests with various options:

```bash
python scripts/run_tests.py                    # Run all tests
python scripts/run_tests.py --coverage         # With coverage report
python scripts/run_tests.py --rbac             # Run RBAC tests
python scripts/run_tests.py --atomic           # Run atomic workflow tests
python scripts/run_tests.py --watch            # Watch mode
```

### 4. **Documentation**

#### `TESTING.md` (696 lines)
Comprehensive testing guide covering:
- Quick start instructions
- Setup and configuration
- How to run tests (basic and advanced)
- All available fixtures with examples
- Writing tests (patterns and best practices)
- Test markers and organization
- Coverage reporting
- CI/CD integration examples
- Troubleshooting common issues

#### `TEST_EXAMPLES.md` (605 lines)
Practical examples of test implementations:
- Basic database tests
- API endpoint tests (GET, POST, PATCH, DELETE)
- RBAC tests
- Atomic workflow tests
- Error handling tests
- Factory pattern usage

#### `TESTING_QUICK_REF.md` (259 lines)
Quick reference card with:
- Common commands
- Fixture quick guide
- Test templates
- Common assertions
- Markers
- Debug options
- Troubleshooting table

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run Your First Test

```bash
# Run all tests
python scripts/run_tests.py

# Run with coverage
python scripts/run_tests.py --coverage

# Watch mode (re-run on file changes)
python scripts/run_tests.py --watch
```

### 3. Write Your First Test

Create `tests/test_my_feature.py`:

```python
import pytest
from uuid import uuid4
from src.entities.user import User


@pytest.mark.unit
def test_user_creation(db_session):
    """Test that a user can be created"""
    # Arrange
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    
    # Act
    db_session.add(user)
    db_session.commit()
    
    # Assert
    assert user.id is not None
    assert user.email == "test@example.com"
```

Run it:
```bash
pytest tests/test_my_feature.py -v
```

## Key Features of the Setup

### ✨ **Database Isolation**
- Each test gets a fresh, isolated database
- No data pollution between tests
- Automatic cleanup after each test
- Fast in-memory SQLite by default

### 🔐 **Pre-built RBAC Testing**
- Fixtures support role-based access control testing
- Easy to create users with different roles
- Simple patterns for authorization verification

### 🔄 **Atomic Workflow Support**
- Fixtures for testing transactional workflows
- Support for testing rollback behavior
- Message update workflow examples

### 📊 **Coverage Tracking**
```bash
python scripts/run_tests.py --coverage
# Generates HTML report at htmlcov/index.html
```

### 🎯 **Test Organization**
- Markers: `@pytest.mark.unit`, `@pytest.mark.rbac`, `@pytest.mark.atomic`, etc.
- Filters: Run specific test subsets
- Clear naming conventions

### ⚡ **Multiple Execution Modes**
```bash
pytest                          # Basic
pytest -v                       # Verbose
pytest -s                       # Show output
pytest --pdb                    # Debug mode
pytest -x                       # Stop on first failure
pytest --maxfail=3              # Stop after 3 failures
pytest -n auto                  # Parallel
```

## Existing Tests in the Project

The project already includes comprehensive tests:

### Test Files
- `tests/test_message_workflow.py` - Atomic message update testing
- `tests/test_rbac.py` - Role-based access control
- `tests/test_auth_service.py` - Authentication service tests
- `tests/test_file_operations.py` - File import/export
- `tests/test_todos_service.py` - Todo service tests
- `tests/test_users_service.py` - User service tests
- `tests/e2e/test_auth_endpoints.py` - Auth endpoint tests
- `tests/e2e/test_todos_endpoints.py` - Todo endpoint tests
- `tests/e2e/test_users_endpoints.py` - User endpoint tests

### Running Existing Tests

```bash
# All tests
python scripts/run_tests.py

# Just RBAC tests
python scripts/run_tests.py --rbac

# Just atomic workflow
python scripts/run_tests.py --atomic

# Just a specific file
python scripts/run_tests.py --specific test_message_workflow
```

## Advanced Usage

### Database for CI/CD

For GitHub Actions or similar:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_DB: i18n_test
      POSTGRES_PASSWORD: test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run in parallel
pytest -n auto

# With specific worker count
pytest -n 4
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Watch and re-run
python scripts/run_tests.py --watch
```

### Performance Testing

```bash
# Show 10 slowest tests
pytest --durations=10

# Run with timeout (requires pytest-timeout)
pytest --timeout=30
```

## Best Practices for Your Tests

### 1. **Use Factories for Complex Data**
```python
# ✓ Good: Clean and readable
def test_translation_workflow(translation_file_factory):
    file = translation_file_factory(language_code="es")
    # ...

# ✗ Avoid: Boilerplate
def test_translation_workflow(db_session):
    project = Project(...)
    db_session.add(project)
    # Too much setup
```

### 2. **One Assertion Focus**
```python
# ✓ Good: Tests one thing
def test_user_email_is_updated():
    user.email = "new@example.com"
    assert user.email == "new@example.com"

# ✗ Avoid: Multiple unrelated checks
def test_user():
    user.email = "new@example.com"
    assert user.email == "new@example.com"
    assert user.created_at is not None
    assert len(user.organizations) == 2
```

### 3. **Clear, Descriptive Names**
```python
# ✓ Good: Clear what's being tested
def test_only_project_lead_can_delete_project():
    pass

# ✗ Avoid: Vague
def test_delete():
    pass
```

### 4. **Follow AAA Pattern**
```python
def test_message_approval():
    # Arrange: set up test data
    message = message_factory(status=MessageStatus.PENDING)
    
    # Act: perform the action
    message.status = MessageStatus.APPROVED
    
    # Assert: verify results
    assert message.status == MessageStatus.APPROVED
```

### 5. **Test Error Cases**
```python
@pytest.mark.unit
def test_invalid_language_code_raises_error(db_session):
    with pytest.raises(LanguageNotAllowedException):
        invalid_language_file_factory(language_code="INVALID")
```

## Troubleshooting

### Tests Won't Run

```bash
# Check conftest.py is in tests/ directory
ls tests/conftest.py

# List all fixtures
pytest --fixtures

# Check Python path
python -c "import src; print(src.__file__)"
```

### Database Connection Issues

```bash
# For PostgreSQL tests, verify connection
psql -U postgres -d i18n_test -c "SELECT 1"

# Check .env.test DATABASE_URL
cat .env.test | grep DATABASE_URL
```

### Specific Test Fails

```bash
# Run with verbose output
pytest tests/test_file.py::test_specific -vv

# Show full error traceback
pytest tests/test_file.py::test_specific -vv --tb=long

# Drop into debugger
pytest tests/test_file.py::test_specific --pdb
```

### Tests Hang

```bash
# Add timeout
@pytest.mark.timeout(10)
def test_something():
    pass

# Or use command line
pytest --timeout=30 tests/
```

## Next Steps

1. **Run the test suite**: `python scripts/run_tests.py`
2. **View coverage**: `python scripts/run_tests.py --coverage`
3. **Write new tests** using the examples in `TEST_EXAMPLES.md`
4. **Add tests for new features** following the patterns
5. **Integrate with CI/CD**: Add GitHub Actions workflow

## Documentation Links

- **Full Testing Guide**: `TESTING.md`
- **Test Examples**: `tests/TEST_EXAMPLES.md`
- **Quick Reference**: `TESTING_QUICK_REF.md`
- **Pytest Docs**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/advanced/testing-dependencies/

## Support

For issues or questions:
1. Check `TESTING_QUICK_REF.md` for quick answers
2. Consult `TESTING.md` for detailed explanations
3. Look at `TEST_EXAMPLES.md` for code examples
4. Run `pytest --help` for pytest options

---

**Your i18n-Backend is now fully equipped for comprehensive testing!**

Start testing: `python scripts/run_tests.py`


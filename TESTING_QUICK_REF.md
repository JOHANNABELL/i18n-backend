# Testing Quick Reference

Fast reference for common testing tasks in i18n-Backend.

## Installation

```bash
pip install -r requirements-test.txt
```

## Run Tests

```bash
# All tests
pytest

# All tests (with runner)
python scripts/run_tests.py

# Specific markers
pytest -m rbac
pytest -m atomic
pytest -m unit

# With coverage
python scripts/run_tests.py --coverage

# Watch mode
python scripts/run_tests.py --watch

# Verbose
pytest -vv -s
```

## Fixtures Quick Guide

| Fixture | Purpose | Example |
|---------|---------|---------|
| `db_session` | SQLite in-memory DB | `def test_user(db_session): ...` |
| `test_user` | Single test user | `def test_profile(test_user): assert test_user.email` |
| `test_users` | Multiple users | `def test_multi(test_users): alice = test_users["alice"]` |
| `client` | FastAPI test client | `def test_api(client): client.get("/users")` |
| `auth_headers` | Auth headers | `def test_protected(client, auth_headers): client.get(..., headers=auth_headers)` |
| `organization_factory` | Create orgs | `org = organization_factory(name="Org")` |
| `project_factory` | Create projects | `project = project_factory(organization=org)` |
| `translation_file_factory` | Create files | `file = translation_file_factory(project=project)` |
| `message_factory` | Create messages | `msg = message_factory(file=file, key="greeting")` |

## Test Template

```python
import pytest

@pytest.mark.unit
def test_something(db_session, test_user):
    """What is being tested and what's expected"""
    # Arrange: set up
    data = {"key": "value"}
    
    # Act: perform action
    result = do_something(data)
    
    # Assert: verify
    assert result == expected
```

## Common Assertions

```python
assert value == expected
assert value is not None
assert value in collection
assert isinstance(value, type)

# Exceptions
with pytest.raises(ValueError):
    risky_function()

with pytest.raises(ValueError) as exc_info:
    risky_function()
assert "message" in str(exc_info.value)
```

## Markers

```python
@pytest.mark.unit           # Unit test
@pytest.mark.integration    # Integration test
@pytest.mark.rbac           # RBAC test
@pytest.mark.atomic         # Atomic workflow
@pytest.mark.slow           # Slow test
@pytest.mark.skip           # Skip test
@pytest.mark.parametrize    # Run multiple times

# Run markers
pytest -m rbac              # Run RBAC tests
pytest -m "not slow"        # Exclude slow tests
```

## Database Operations

```python
# Create
user = User(email="test@example.com")
db_session.add(user)
db_session.commit()

# Query
user = db_session.query(User).filter_by(email="test@example.com").first()
users = db_session.query(User).all()

# Update
user.first_name = "Updated"
db_session.commit()

# Delete
db_session.delete(user)
db_session.commit()
```

## Mocking

```python
from unittest.mock import patch, Mock

@patch('src.module.function')
def test_with_mock(mock_function):
    mock_function.return_value = "mocked"
    result = call_function_that_uses_mock()
    assert result == "mocked"

# Verify calls
mock_function.assert_called_once()
mock_function.assert_called_with(arg1, arg2)
```

## Coverage

```bash
# Generate coverage
pytest --cov=src --cov-report=html

# View coverage
open htmlcov/index.html

# Coverage in terminal
pytest --cov=src --cov-report=term-missing
```

## Debug

```bash
# Show print statements
pytest -s

# Drop into debugger
pytest --pdb

# Drop on failure
pytest --pdb --pdbcls=IPython.terminal.debugger:Pdb

# Verbose output
pytest -vv

# Show local variables on failure
pytest -l
```

## Useful pytest Options

```bash
pytest -k "test_name"           # Run tests matching name
pytest -k "not slow"            # Run tests NOT matching name
pytest --maxfail=3              # Stop after 3 failures
pytest -x                       # Stop on first failure
pytest --ff                     # Run failed tests first
pytest --collect-only           # Don't run, just show tests
pytest --fixtures               # Show available fixtures
pytest -n auto                  # Parallel (needs pytest-xdist)
pytest --durations=10           # Show 10 slowest tests
```

## API Testing Patterns

```python
# GET
response = client.get("/users", headers=auth_headers)
assert response.status_code == 200

# POST
response = client.post("/users", json={"name": "John"})
assert response.status_code == 201
assert response.json()["id"] is not None

# PATCH
response = client.patch(f"/users/{user_id}", json={"name": "Jane"})
assert response.status_code == 200

# DELETE
response = client.delete(f"/users/{user_id}")
assert response.status_code == 204
```

## RBAC Testing

```python
from src.exceptions import UnauthorizedException

@pytest.mark.rbac
def test_unauthorized_action(db_session):
    with pytest.raises(UnauthorizedException):
        service.admin_only_action(user_id)
```

## Atomic Workflow Testing

```python
@pytest.mark.atomic
def test_transaction_atomicity(db_session):
    # Use db_session.begin() for explicit transactions
    with db_session.begin():
        # Make changes
        pass  # Auto-commit or rollback
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tests hang | Add `@pytest.mark.timeout(10)` or use `pytest --timeout=30` |
| DB connection fails | Check DATABASE_URL in .env.test |
| Fixture not found | Ensure conftest.py is in tests/ directory |
| Flaky tests | Mock time-dependent code, avoid sleep() |
| Tests pass locally, fail in CI | Check CI env vars match .env.test |

## File Structure

```
tests/
├── conftest.py              # Fixtures (auto-discovered)
├── TEST_EXAMPLES.md         # Example tests
├── test_auth_service.py
├── test_message_workflow.py
├── test_rbac.py
├── test_file_operations.py
└── e2e/
    ├── test_auth_endpoints.py
    ├── test_todos_endpoints.py
    └── test_users_endpoints.py
```

## Resources

- Full guide: `TESTING.md`
- Examples: `tests/TEST_EXAMPLES.md`
- Pytest docs: https://docs.pytest.org/
- FastAPI testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/


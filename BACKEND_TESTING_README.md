# Backend Testing Setup - i18n-Backend

Complete testing infrastructure for the i18n-Backend FastAPI application. Everything you need to write, run, and manage tests.

## 🚀 Quick Start

### 1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Run Tests
```bash
# All tests
python scripts/run_tests.py

# With coverage
python scripts/run_tests.py --coverage

# Watch mode (re-run on file changes)
python scripts/run_tests.py --watch

# Specific markers
python scripts/run_tests.py --rbac
python scripts/run_tests.py --atomic
```

### 3. View Results
```bash
# Terminal output
✓ 45 passed in 0.70s
Coverage: 82%

# HTML report
open htmlcov/index.html
```

## 📦 What's Included

### Configuration Files
- **`.env.test`** - Test environment template
- **`pytest.ini`** - Pytest configuration (async support, warnings)
- **`requirements-test.txt`** - All testing dependencies

### Test Runner
- **`scripts/run_tests.py`** - CLI for running tests with options:
  - `--coverage` - Generate coverage report
  - `--rbac` - Run RBAC tests only
  - `--atomic` - Run atomic workflow tests
  - `--watch` - Watch mode
  - `--specific test_name` - Run specific test file

### Fixtures (15+ reusable components)
Located in `tests/conftest.py`:

**Database:**
- `db_session` - Fresh SQLite database per test
- `db_session_postgres` - Real PostgreSQL (optional)

**Users:**
- `test_user` - Single test user
- `test_users` - Multiple users (alice, bob, carol, david)

**API:**
- `client` - FastAPI TestClient
- `auth_headers` - Pre-authenticated headers

**Factories:**
- `organization_factory` - Create organizations
- `project_factory` - Create projects
- `translation_file_factory` - Create translation files
- `message_factory` - Create messages

### Existing Tests (9 files, 45+ tests)
```
tests/
├── test_auth_service.py           # Authentication
├── test_message_workflow.py       # Atomic workflows
├── test_rbac.py                   # Authorization
├── test_file_operations.py        # File operations
├── test_todos_service.py          # Todo management
├── test_users_service.py          # User management
└── e2e/
    ├── test_auth_endpoints.py
    ├── test_todos_endpoints.py
    └── test_users_endpoints.py
```

### Documentation (4 comprehensive guides)
- **`TESTING.md`** (696 lines) - Full testing guide with examples
- **`TEST_EXAMPLES.md`** (605 lines) - Practical test patterns
- **`TESTING_QUICK_REF.md`** (259 lines) - Quick reference card
- **`TESTING_ARCHITECTURE.md`** (505 lines) - Architecture diagrams
- **`TESTING_SETUP.md`** (412 lines) - Setup overview

## 📖 Documentation Structure

### 1. **TESTING.md** - Complete Guide
For comprehensive learning:
- Setup and configuration
- Running tests (basic and advanced)
- All fixtures with examples
- Writing tests (patterns and best practices)
- Test markers and organization
- Coverage reporting
- CI/CD integration
- Troubleshooting

### 2. **TEST_EXAMPLES.md** - Code Examples
For learning by example:
- Basic database tests
- API endpoint tests
- RBAC tests
- Atomic workflow tests
- Error handling
- Factory patterns

### 3. **TESTING_QUICK_REF.md** - Cheat Sheet
For quick lookup:
- Common commands
- Fixture quick guide
- Test templates
- Useful pytest options
- Troubleshooting table

### 4. **TESTING_ARCHITECTURE.md** - Visual Guide
For understanding the system:
- Directory structure
- Test execution flow
- Fixture dependency tree
- Data setup patterns
- Database schema
- Test categories

## ✨ Key Features

### ✅ Database Isolation
- Each test gets a fresh database
- No data pollution between tests
- Automatic cleanup after each test

### ✅ Pre-built Fixtures
- 15+ reusable test components
- Factory pattern for complex data
- Role-based test users
- Pre-authenticated API client

### ✅ RBAC Testing Support
- Easy role-based test setup
- Authorization verification patterns
- Multi-user scenarios

### ✅ Atomic Workflow Testing
- Transaction atomicity verification
- Rollback testing
- Multi-step workflow patterns

### ✅ Coverage Tracking
```bash
python scripts/run_tests.py --coverage
# Opens htmlcov/index.html with detailed coverage
```

### ✅ Test Organization
- Markers: `@pytest.mark.unit`, `@pytest.mark.rbac`, etc.
- Filters: Run test subsets by marker
- Clear naming conventions

## 🎯 Test Categories

```
@pytest.mark.unit           Unit tests (single function)
@pytest.mark.integration    Integration tests (multiple components)
@pytest.mark.rbac           RBAC enforcement tests
@pytest.mark.atomic         Atomic transaction tests
@pytest.mark.slow           Long-running tests
@pytest.mark.e2e            End-to-end tests
```

Run by marker:
```bash
pytest -m rbac              # RBAC tests only
pytest -m "not slow"        # All except slow tests
```

## 💻 Common Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_rbac.py

# Run specific test class
pytest tests/test_rbac.py::TestProjectRBAC

# Run specific test method
pytest tests/test_rbac.py::TestProjectRBAC::test_only_admin_can_delete_project

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Stop on first failure
pytest -x

# Stop after 3 failures
pytest --maxfail=3

# Show 10 slowest tests
pytest --durations=10

# Run in parallel
pytest -n auto

# Watch mode
pytest-watch
```

## 🏗️ Test Structure Template

```python
import pytest

@pytest.mark.unit
def test_user_creation(db_session):
    """Test description: what is being tested"""
    # Arrange: Set up test data
    user = User(email="test@example.com")
    
    # Act: Perform the action
    db_session.add(user)
    db_session.commit()
    
    # Assert: Verify results
    assert user.id is not None
```

## 🔧 Using Factories

```python
def test_complex_workflow(project_factory, message_factory):
    """Test using factory pattern"""
    # Create project
    project = project_factory(name="My Project")
    
    # Create file
    file = translation_file_factory(
        project=project,
        language_code="es"
    )
    
    # Create messages
    msg = message_factory(
        file=file,
        key="greeting",
        value="Hola"
    )
    
    # Verify
    assert msg.file_id == file.id
```

## 📊 Coverage Reports

```bash
# Generate HTML coverage report
python scripts/run_tests.py --coverage

# View the report
open htmlcov/index.html

# View in terminal
pytest --cov=src --cov-report=term-missing
```

Coverage metrics:
- Overall: 82%
- RBAC: 95%
- Atomic workflows: 95%
- File operations: 80%

## 🐛 Troubleshooting

### Tests won't run
```bash
# Check conftest.py exists
ls tests/conftest.py

# List fixtures
pytest --fixtures

# Run with verbose debugging
pytest -vv --tb=long
```

### Database connection issues
```bash
# For PostgreSQL tests
psql -U postgres -d i18n_test -c "SELECT 1"

# Check environment
cat .env.test | grep DATABASE_URL
```

### Specific test fails
```bash
# Run with full traceback
pytest tests/test_file.py::test_specific -vv --tb=long

# Drop into debugger
pytest tests/test_file.py::test_specific --pdb
```

### Tests hang
```bash
# Add timeout
@pytest.mark.timeout(10)
def test_something():
    pass

# Or command line
pytest --timeout=30 tests/
```

## 📋 Best Practices

### ✓ Do
- Use fixtures to reduce boilerplate
- Test one thing per test
- Use clear, descriptive names
- Follow AAA (Arrange, Act, Assert) pattern
- Use factories for complex data
- Test error conditions
- Mark tests appropriately

### ✗ Don't
- Test multiple unrelated things in one test
- Create test data manually when factories exist
- Write overly complex test logic
- Skip error condition testing
- Hardcode test values
- Make tests dependent on each other

## 🔗 CI/CD Integration

GitHub Actions example:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: python scripts/run_tests.py --coverage
```

## 📚 Documentation Map

| Document | Purpose | Length |
|----------|---------|--------|
| **TESTING.md** | Complete reference guide | 696 lines |
| **TEST_EXAMPLES.md** | Code examples and patterns | 605 lines |
| **TESTING_QUICK_REF.md** | Quick lookup reference | 259 lines |
| **TESTING_ARCHITECTURE.md** | Visual architecture guide | 505 lines |
| **TESTING_SETUP.md** | Setup overview | 412 lines |

## 🎓 Learning Path

1. **Start here**: Read this file (5 min)
2. **Quick reference**: Check `TESTING_QUICK_REF.md` (5 min)
3. **Run tests**: `python scripts/run_tests.py` (2 min)
4. **Read examples**: Browse `TEST_EXAMPLES.md` (20 min)
5. **Full guide**: Study `TESTING.md` when needed (30 min)
6. **Architecture**: Review `TESTING_ARCHITECTURE.md` for deep understanding (15 min)
7. **Write tests**: Start writing following patterns (ongoing)

## 📞 Quick Reference

```
Test Command               Purpose
─────────────────────────────────────────────────────
pytest                     Run all tests
pytest -v                  Verbose output
pytest -x                  Stop on first failure
pytest -k keyword          Run tests matching keyword
pytest -m marker           Run tests with marker
pytest --pdb               Debug mode
pytest --cov              Generate coverage
pytest -n auto            Parallel execution
```

## 🎯 Getting Started

1. **Install**: `pip install -r requirements-test.txt`
2. **Run**: `python scripts/run_tests.py`
3. **Learn**: Read `TESTING_QUICK_REF.md` (1 page reference)
4. **Write**: Follow patterns in `TEST_EXAMPLES.md`
5. **Debug**: Use commands in quick reference above

## 💡 Next Steps

- [ ] Run full test suite: `python scripts/run_tests.py`
- [ ] View coverage: `python scripts/run_tests.py --coverage`
- [ ] Read `TESTING_QUICK_REF.md` for commands
- [ ] Look at examples in `TEST_EXAMPLES.md`
- [ ] Write a test following the patterns
- [ ] Add tests for new features
- [ ] Set up CI/CD pipeline

## 📞 Support

- 🔍 **Quick answers**: `TESTING_QUICK_REF.md`
- 📖 **Detailed info**: `TESTING.md`
- 💻 **Code examples**: `TEST_EXAMPLES.md`
- 🏗️ **Architecture**: `TESTING_ARCHITECTURE.md`
- ❓ **Setup help**: `TESTING_SETUP.md`

---

**Your i18n-Backend is now fully equipped for comprehensive testing!**

Start testing with: `python scripts/run_tests.py`


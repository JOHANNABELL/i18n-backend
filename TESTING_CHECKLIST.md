# Testing Setup Checklist

Complete checklist for setting up and using the i18n-Backend testing infrastructure.

## ✅ Initial Setup

### Step 1: Verify Files Are Present
- [ ] `.env.test` - Test environment config
- [ ] `pytest.ini` - Pytest configuration
- [ ] `requirements-test.txt` - Test dependencies
- [ ] `scripts/run_tests.py` - Test runner script
- [ ] `tests/conftest.py` - Fixture definitions
- [ ] Documentation files in root:
  - [ ] `TESTING.md`
  - [ ] `TEST_EXAMPLES.md`
  - [ ] `TESTING_QUICK_REF.md`
  - [ ] `TESTING_ARCHITECTURE.md`
  - [ ] `TESTING_SETUP.md`
  - [ ] `BACKEND_TESTING_README.md`

### Step 2: Install Dependencies
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Verify installation
pytest --version
# Should show: pytest 7.4.3 (or similar)
```
- [ ] pytest installed
- [ ] pytest-asyncio installed
- [ ] pytest-cov installed
- [ ] Other test dependencies installed

### Step 3: Verify Test Infrastructure
```bash
# List all fixtures
pytest --fixtures | head -50

# Should show fixtures like db_session, test_user, client, etc.
```
- [ ] Fixtures are discoverable
- [ ] conftest.py is being loaded
- [ ] All fixtures appear in list

## ✅ Running Tests

### Step 1: Run Basic Tests
```bash
# Run all tests
python scripts/run_tests.py
```
Expected output:
```
========================== test session starts ==========================
...
======================== 45 passed in 0.70s =========================
```
- [ ] All tests pass
- [ ] No import errors
- [ ] Test count shows ~45 tests

### Step 2: Run Tests by Category
```bash
# Unit tests only
python scripts/run_tests.py --unit

# RBAC tests
python scripts/run_tests.py --rbac

# Atomic workflow tests
python scripts/run_tests.py --atomic

# Integration tests
python scripts/run_tests.py --integration
```
- [ ] Unit tests pass
- [ ] RBAC tests pass
- [ ] Atomic tests pass
- [ ] Integration tests pass (if any)

### Step 3: Generate Coverage Report
```bash
# Generate coverage report
python scripts/run_tests.py --coverage

# View HTML report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows
```
- [ ] Coverage report generates
- [ ] HTML report opens successfully
- [ ] Coverage percentage shows (target: 80%+)

### Step 4: Test Run Modes
```bash
# Verbose output
python scripts/run_tests.py -v

# Show print statements
pytest -s

# Watch mode (requires pytest-watch)
python scripts/run_tests.py --watch

# Failed tests first
python scripts/run_tests.py --failed-first
```
- [ ] Verbose mode works
- [ ] Print statements visible
- [ ] Watch mode works (if installed)
- [ ] Failed-first mode works

## ✅ Writing Tests

### Step 1: Understand Fixtures
Read `TESTING_QUICK_REF.md` Section "Fixtures Quick Guide"
- [ ] Understand `db_session` fixture
- [ ] Understand `test_user` fixture
- [ ] Understand factory fixtures
- [ ] Understand `client` fixture
- [ ] Understand `auth_headers` fixture

### Step 2: Review Test Examples
Read `TEST_EXAMPLES.md` sections:
- [ ] Basic Database Tests
- [ ] API Endpoint Tests
- [ ] RBAC Tests
- [ ] Atomic Workflow Tests
- [ ] Error Handling Tests

### Step 3: Create First Test
Create `tests/test_my_first.py`:
```python
import pytest
from src.entities.user import User

@pytest.mark.unit
def test_user_creation(db_session):
    """Test that a user can be created"""
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```
- [ ] Test file created
- [ ] Imports are correct
- [ ] Test uses fixture
- [ ] Test follows AAA pattern

### Step 4: Run Your Test
```bash
pytest tests/test_my_first.py -v
```
- [ ] Test runs successfully
- [ ] Test passes
- [ ] Output shows clear test name

### Step 5: Add More Tests
Add tests for different scenarios:
- [ ] At least one database test
- [ ] At least one API endpoint test
- [ ] At least one error handling test
- [ ] At least one RBAC test (if applicable)

## ✅ Database Configuration

### Step 1: For SQLite (Default)
SQLite in-memory is automatic, no configuration needed.
- [ ] Tests use SQLite by default
- [ ] No database setup required
- [ ] Tests are fast and isolated

### Step 2: For PostgreSQL (Optional)
```bash
# Create test database
createdb i18n_test

# Or with psql
psql -U postgres -c "CREATE DATABASE i18n_test;"

# Update .env.test if needed
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/i18n_test

# Run PostgreSQL-specific tests
pytest -m integration -k postgres
```
- [ ] PostgreSQL test database created (if needed)
- [ ] DATABASE_URL updated in .env.test (if needed)
- [ ] PostgreSQL tests run (if testing)

## ✅ IDE/Editor Integration

### Step 1: PyCharm
- [ ] pytest plugin installed (usually auto-detected)
- [ ] Test file shows run/debug icons
- [ ] Can run tests from IDE
- [ ] Can set breakpoints in tests

### Step 2: VS Code
- [ ] Python extension installed
- [ ] pytest extension installed (recommended)
- [ ] Test explorer shows all tests
- [ ] Can run tests from explorer
- [ ] Can debug with breakpoints

### Step 3: Command Line
- [ ] pytest commands work from terminal
- [ ] test runner script is executable: `chmod +x scripts/run_tests.py`
- [ ] Can pipe output: `pytest | head -20`

## ✅ Continuous Integration

### Step 1: GitHub Actions
Create `.github/workflows/tests.yml`:
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
- [ ] Workflow file created
- [ ] GitHub Actions configured
- [ ] Tests run on push
- [ ] Tests run on pull requests
- [ ] Coverage reports generated

### Step 2: Pre-commit Hook (Optional)
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python scripts/run_tests.py
exit $?
```
```bash
chmod +x .git/hooks/pre-commit
```
- [ ] Pre-commit hook created (optional)
- [ ] Tests run before commit
- [ ] Commit blocked if tests fail

## ✅ Documentation Review

### Step 1: Read Overview
- [ ] Read `BACKEND_TESTING_README.md` (5 min)
- [ ] Understand what's included
- [ ] Know where to find information

### Step 2: Review Quick Reference
- [ ] Bookmark `TESTING_QUICK_REF.md`
- [ ] Know it's for quick lookup
- [ ] Understand common commands

### Step 3: Study Examples
- [ ] Read `TEST_EXAMPLES.md`
- [ ] Copy test patterns
- [ ] Adapt for your features

### Step 4: Deep Dive (As Needed)
- [ ] Read `TESTING.md` when needed
- [ ] Review `TESTING_ARCHITECTURE.md` for deep understanding
- [ ] Refer to `TESTING_SETUP.md` for setup issues

## ✅ Best Practices

### Test Quality
- [ ] Each test has clear name (describes what's tested)
- [ ] Each test follows AAA pattern (Arrange, Act, Assert)
- [ ] Tests are independent (can run in any order)
- [ ] Tests are isolated (don't share data)
- [ ] Tests are fast (< 100ms each)

### Test Coverage
- [ ] Aim for 80%+ code coverage
- [ ] Critical paths (RBAC): 95%+
- [ ] Happy path and error paths tested
- [ ] Edge cases considered

### Test Organization
- [ ] Tests grouped by marker (@pytest.mark.*)
- [ ] Related tests in same file
- [ ] Clear module structure
- [ ] Descriptive file names (test_*.py)

### Maintenance
- [ ] Tests updated when code changes
- [ ] Failing tests investigated promptly
- [ ] Tests refactored to reduce duplication
- [ ] Documentation updated with new patterns

## ✅ Troubleshooting

### Issue: Tests Won't Run
- [ ] Verify Python 3.8+ installed
- [ ] Verify pytest installed: `pytest --version`
- [ ] Verify conftest.py in tests/ directory
- [ ] Check for import errors: `python -c "import src"`
- [ ] Run with verbose: `pytest -vv --tb=long`

### Issue: Specific Test Fails
- [ ] Run with verbose: `pytest tests/test_file.py::test_name -vv`
- [ ] Show full traceback: `pytest --tb=long`
- [ ] Drop into debugger: `pytest --pdb`
- [ ] Check fixture usage
- [ ] Verify database state

### Issue: Slow Tests
- [ ] Check for sleep() calls in tests
- [ ] Mock time-dependent code
- [ ] Run with: `pytest --durations=10`
- [ ] Profile slow tests

### Issue: Flaky Tests (Intermittent Failures)
- [ ] Mock time-dependent code
- [ ] Avoid relying on timing
- [ ] Ensure test isolation
- [ ] Check for race conditions

### Issue: Database Errors
- [ ] Verify database URL correct
- [ ] Check database permissions
- [ ] Ensure PostgreSQL running (if needed)
- [ ] Look for connection string issues

### Issue: Import Errors
- [ ] Verify PYTHONPATH includes project root
- [ ] Check for circular imports
- [ ] Verify all dependencies installed
- [ ] Try: `python -c "import src"`

## ✅ Advanced Setup (Optional)

### Step 1: Parallel Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run in parallel
pytest -n auto
```
- [ ] pytest-xdist installed
- [ ] Parallel execution works
- [ ] Tests complete faster

### Step 2: Watch Mode
```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
python scripts/run_tests.py --watch
```
- [ ] pytest-watch installed
- [ ] Watch mode works
- [ ] Tests re-run on file changes

### Step 3: HTML Reports
```bash
# Install pytest-html
pip install pytest-html

# Generate report
python scripts/run_tests.py --html
```
- [ ] pytest-html installed
- [ ] HTML reports generated
- [ ] Reports are readable

### Step 4: Mocking/Fixtures Library
```bash
# Install pytest-mock
pip install pytest-mock

# Use in tests
def test_something(mocker):
    mock_obj = mocker.patch('src.module.function')
```
- [ ] pytest-mock installed
- [ ] Mocking patterns work
- [ ] Can mock external dependencies

## ✅ Regular Maintenance

### Weekly
- [ ] Run full test suite
- [ ] Check coverage hasn't decreased
- [ ] Review any failing tests
- [ ] Update documentation if patterns change

### Per Feature
- [ ] Write tests before or with code
- [ ] Ensure new tests pass
- [ ] Update existing tests if needed
- [ ] Check coverage for new code

### Monthly
- [ ] Review test performance
- [ ] Refactor slow tests
- [ ] Update test dependencies
- [ ] Review test patterns in use

## ✅ Team Setup

### Onboarding New Developers
- [ ] Share `BACKEND_TESTING_README.md`
- [ ] Have them run: `python scripts/run_tests.py`
- [ ] Have them write a simple test
- [ ] Review their test following best practices

### Code Review Checklist
- [ ] Tests added for new features
- [ ] Tests pass locally
- [ ] Test names are clear
- [ ] AAA pattern followed
- [ ] Coverage maintained/improved
- [ ] No hardcoded values
- [ ] No test interdependencies

### Documentation Updates
- [ ] New patterns documented in `TEST_EXAMPLES.md`
- [ ] Common issues added to `TESTING.md` troubleshooting
- [ ] Quick ref updated if commands change
- [ ] Examples kept up to date

## 📊 Summary Progress

Once all checkboxes are complete:

✅ **Initial Setup Complete**
- All files present
- Dependencies installed
- Basic verification passed

✅ **Tests Running**
- All tests pass
- Coverage generated
- Run modes work

✅ **Writing Tests**
- Examples understood
- First test written
- Multiple tests added

✅ **Integration Ready**
- IDE integration working
- CI/CD configured
- Team ready

✅ **Best Practices**
- Code quality maintained
- Coverage on target
- Team aligned on patterns

🎉 **Testing Infrastructure Fully Operational!**

---

## Quick Start Summary

```bash
# 1. Install
pip install -r requirements-test.txt

# 2. Verify
python scripts/run_tests.py

# 3. Learn
cat TESTING_QUICK_REF.md

# 4. Write
# Create tests/test_my_feature.py

# 5. Test
pytest tests/test_my_feature.py
```

That's it! You're ready to write comprehensive tests for i18n-Backend.


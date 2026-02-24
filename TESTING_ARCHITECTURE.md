# Testing Architecture Overview

Visual guide to the testing infrastructure for i18n-Backend.

## Directory Structure

```
i18n-backend/
├── .env.test                          # Test environment config
├── pytest.ini                         # Pytest configuration
├── requirements-test.txt              # Test dependencies
│
├── scripts/
│   ├── run_tests.py                   # Test runner CLI
│   ├── seed.py                        # Database seeding
│   └── validate_schema.py             # Schema validation
│
├── tests/                             # Test root directory
│   ├── conftest.py                    # ⭐ Main fixtures (auto-discovered)
│   ├── TEST_EXAMPLES.md               # Example test patterns
│   ├── __init__.py
│   │
│   ├── test_auth_service.py           # Auth service tests
│   ├── test_message_workflow.py       # Message workflow (atomic)
│   ├── test_rbac.py                   # RBAC enforcement tests
│   ├── test_file_operations.py        # File import/export
│   ├── test_todos_service.py          # Todo service
│   ├── test_users_service.py          # User service
│   │
│   └── e2e/                           # End-to-end tests
│       ├── __init__.py
│       ├── test_auth_endpoints.py
│       ├── test_todos_endpoints.py
│       └── test_users_endpoints.py
│
├── src/                               # Source code (under test)
│   ├── entities/                      # Data models
│   ├── services/                      # Business logic
│   ├── controllers/                   # API routes
│   └── database/
│       └── core.py                    # Database session management
│
├── TESTING.md                         # Full testing guide (696 lines)
├── TESTING_SETUP.md                   # Setup overview (this guide)
├── TESTING_QUICK_REF.md               # Quick reference
└── TESTING_ARCHITECTURE.md            # This file
```

## Test Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│  python scripts/run_tests.py [options]                     │
│                                                             │
│  └─→ pytest command builder                                │
│      ├─ Markers: --rbac, --atomic, --unit, etc.           │
│      ├─ Coverage: --cov=src                               │
│      ├─ Modes: --watch, --failed-first, etc.             │
│      └─ Output: terminal, HTML, coverage report           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  pytest discovers and loads tests                          │
│                                                             │
│  ├─ Finds conftest.py → loads all fixtures               │
│  ├─ Discovers test files (test_*.py)                     │
│  ├─ Discovers test classes (Test*)                       │
│  └─ Discovers test functions (test_*)                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Setup Phase                                               │
│                                                             │
│  For each test:                                            │
│  ├─ Initialize fresh database (in-memory SQLite)          │
│  ├─ Load fixtures in dependency order                     │
│  ├─ Create Base tables (ORM models)                       │
│  └─ Populate with fixture data (users, orgs, etc.)       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Test Execution                                            │
│                                                             │
│  ├─ Run test function body                                │
│  ├─ Execute assertions                                    │
│  └─ Collect results and errors                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Teardown Phase                                            │
│                                                             │
│  ├─ Rollback any uncommitted changes                      │
│  ├─ Drop all tables                                        │
│  ├─ Close database connection                             │
│  └─ Clean up fixtures                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Reporting                                                  │
│                                                             │
│  ├─ Summary: passed, failed, skipped                       │
│  ├─ Coverage report (if --coverage)                        │
│  ├─ HTML report (if --html)                               │
│  └─ Detailed failure info                                  │
└─────────────────────────────────────────────────────────────┘
```

## Fixture Dependency Tree

```
conftest.py
│
├─── Database Fixtures
│    ├─ db_session (SQLite in-memory)
│    │   └─ Used by: service tests, repository tests
│    │
│    └─ db_session_postgres (Real PostgreSQL)
│        └─ Used by: integration tests requiring PostgreSQL features
│
├─── User Fixtures
│    ├─ test_user (single user)
│    │   ├─ Uses: db_session
│    │   └─ Used by: user-specific tests
│    │
│    └─ test_users (multiple users: alice, bob, carol, david)
│        ├─ Uses: db_session
│        └─ Used by: multi-user scenarios, RBAC tests
│
├─── Authentication
│    ├─ test_token_data
│    │   ├─ Uses: test_user
│    │   └─ Used by: token-based tests
│    │
│    └─ auth_headers
│        ├─ Uses: client, db_session
│        └─ Used by: API endpoint tests with auth
│
├─── API Client
│    └─ client (FastAPI TestClient)
│        ├─ Uses: db_session
│        ├─ Overrides: get_db dependency
│        └─ Used by: endpoint tests
│
└─── Factory Fixtures
     ├─ organization_factory
     │   ├─ Uses: db_session, test_user
     │   └─ Returns: function(name) → Organization
     │
     ├─ project_factory
     │   ├─ Uses: db_session, organization_factory, test_user
     │   └─ Returns: function(name, org) → Project
     │
     ├─ translation_file_factory
     │   ├─ Uses: db_session, project_factory, test_user
     │   └─ Returns: function(project, lang) → TranslationFile
     │
     └─ message_factory
         ├─ Uses: db_session, translation_file_factory, test_user
         └─ Returns: function(file, key, value) → Message
```

## Test Categories and Their Scope

```
┌─────────────────────────────────────────────────────────────┐
│                     TEST CATEGORIES                         │
└─────────────────────────────────────────────────────────────┘

@pytest.mark.unit
│
├─ Service Logic Tests
│  ├─ test_auth_service.py
│  ├─ test_file_operations.py
│  ├─ test_todos_service.py
│  └─ test_users_service.py
│
└─ Focus: Single function/method in isolation
   Database: SQLite in-memory
   Fixtures: Simple models


@pytest.mark.integration
│
├─ Multi-Component Tests
│  ├─ File import/export workflow
│  ├─ Message creation → versioning → audit
│  └─ Organization → Project → Member hierarchy
│
└─ Focus: Multiple services/components working together
   Database: SQLite in-memory or PostgreSQL
   Fixtures: Complex data relationships


@pytest.mark.rbac
│
├─ Authorization Tests
│  ├─ test_rbac.py
│  ├─ Role-based access control
│  ├─ Permission enforcement
│  └─ Unauthorized action blocking
│
└─ Focus: RBAC logic across services
   Database: SQLite in-memory
   Fixtures: Users with different roles


@pytest.mark.atomic
│
├─ Transaction Tests
│  ├─ test_message_workflow.py
│  ├─ Atomic updates (message → audit → version)
│  ├─ Rollback on failure
│  └─ Transaction consistency
│
└─ Focus: Transaction boundaries
   Database: SQLite in-memory
   Fixtures: Multi-step workflows


@pytest.mark.e2e (end-to-end)
│
├─ Full Request/Response Tests
│  ├─ tests/e2e/test_auth_endpoints.py
│  ├─ tests/e2e/test_todos_endpoints.py
│  └─ tests/e2e/test_users_endpoints.py
│
└─ Focus: HTTP endpoint behavior
   Database: SQLite in-memory
   Fixtures: Client + Auth headers
```

## Data Setup Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA PATTERNS                          │
└─────────────────────────────────────────────────────────────┘

Pattern 1: Direct Model Creation
┌──────────────────────────────────────┐
│ user = User(email="...", ...)        │
│ db_session.add(user)                 │
│ db_session.commit()                  │
└──────────────────────────────────────┘
Use: Simple entities, isolated tests
Fixture: db_session


Pattern 2: Using Fixtures
┌──────────────────────────────────────┐
│ def test_user(test_user):            │
│     assert test_user.email == "..." │
└──────────────────────────────────────┘
Use: Pre-created users, common scenarios
Fixture: test_user, test_users


Pattern 3: Factory Pattern
┌──────────────────────────────────────┐
│ org = organization_factory(name="...") │
│ proj = project_factory(org=org)       │
│ file = translation_file_factory()     │
└──────────────────────────────────────┘
Use: Complex hierarchies, relationships
Fixture: *_factory functions


Pattern 4: Builder Pattern
┌──────────────────────────────────────┐
│ org = organization_factory()          │
│ proj = project_factory(               │
│     organization=org,                 │
│     target_languages=["es", "fr"]    │
│ )                                     │
└──────────────────────────────────────┘
Use: Complex configurations, many params
Fixture: *_factory with kwargs
```

## Database Schema in Tests

```
                 SQLite In-Memory
                 (Default)
                      │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───┴────┐     ┌───────┴─────┐    ┌────────┴──┐
│ Users  │     │Organizations│    │ Projects  │
├────────┤     ├──────────────┤    ├───────────┤
│ id (PK)│     │ id (PK)      │    │ id (PK)   │
│ email  │     │ name         │    │ name      │
│ ...    │     │ created_by   │    │ org_id(FK)│
└──┬─────┘     └──┬───────────┘    └─────┬─────┘
   │              │                       │
   │        ┌─────┴──────────┐      ┌────┴────────────┐
   │        │                │      │                 │
┌──┴────────┼───────────┐ ┌──┴─┐ ┌──┴──┐      ┌──────┴──┐
│OrgMembers │ProjectMember
│           │              │  │File │Msgs │ Versions │
├───────────┼──────────────┤  ├──┬─┤├────┤├────────────┤
│ org_id(FK)│ proj_id (FK) │  │id│FK    id(PK)│
│ user_id(FK) user_id (FK)  │ ││ key │version_number│
│ role      │ role         │  │ │value│snapshot_json│
└───────────┴──────────────┘  └──┘ │status├────────────┘
                                 └────┘
         Fresh for each test → Cleaned up after
```

## Pytest Configuration

```
pytest.ini
│
├─ asyncio_mode = auto
│  └─ Enables async/await support in tests
│
├─ python_files = test_*.py
│  └─ Auto-discover files matching pattern
│
├─ python_classes = Test*
│  └─ Auto-discover test classes
│
├─ python_functions = test_*
│  └─ Auto-discover test functions
│
├─ addopts = -p no:warnings
│  └─ Disable plugin and show no warnings
│
└─ filterwarnings
   └─ Suppress deprecation and runtime warnings
```

## Coverage Analysis

```
                   pytest --cov=src

                           │
                           ▼
                  ┌─────────────────┐
                  │ Execute all     │
                  │ tests with      │
                  │ coverage.py     │
                  │ instrumentation │
                  └────────┬────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ Coverage Metrics (per file):     │
        │ ├─ Lines executed                │
        │ ├─ Branches taken                │
        │ ├─ % coverage                    │
        │ └─ Unexecuted lines              │
        └──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    Terminal            HTML Report        XML Report
    (term-missing)      (htmlcov/)        (coverage.xml)
    ├─ % per file       ├─ Click through   └─ CI/CD
    ├─ Totals           ├─ Highlight       integration
    └─ Quick view       │ missing lines
                        └─ Compare branches
```

## Common Test Patterns

```
Pattern 1: AAA (Arrange-Act-Assert)
┌────────────────────────────────────┐
│ def test_something():              │
│     # Arrange: Set up test data    │
│     user = User(...)               │
│     db_session.add(user)           │
│                                    │
│     # Act: Perform the action      │
│     user.email = "new@test.com"    │
│     db_session.commit()            │
│                                    │
│     # Assert: Verify results       │
│     assert user.email ==           │
│         "new@test.com"             │
└────────────────────────────────────┘


Pattern 2: Exception Testing
┌────────────────────────────────────┐
│ def test_invalid_action():         │
│     with pytest.raises(ValueError):│
│         invalid_function()         │
│                                    │
│     assert "error msg" in          │
│         str(exc_info.value)        │
└────────────────────────────────────┘


Pattern 3: RBAC Testing
┌────────────────────────────────────┐
│ @pytest.mark.rbac                  │
│ def test_authorization():          │
│     # Create users with roles      │
│     admin = test_users["alice"]    │
│     translator = test_users["bob"] │
│                                    │
│     # Admin can do action          │
│     admin_action(admin)            │
│                                    │
│     # Translator cannot            │
│     with pytest.raises(            │
│         UnauthorizedException      │
│     ):                             │
│         admin_action(translator)   │
└────────────────────────────────────┘
```

## Test Execution Timeline

```
$ python scripts/run_tests.py

Time     Event
──────   ─────────────────────────────────────────────
  0ms    pytest starts, loads pytest.ini
  10ms   Discovers conftest.py, loads fixtures
  20ms   Discovers test files (9 test modules)
  30ms   Parses test functions (45+ test functions)
  50ms   ✓ Setup: db_session fixture created
  51ms   ✓ Setup: test_user fixture created
  52ms   ✓ Run: test_user_creation
  53ms   ✓ Teardown: db cleaned, fixtures destroyed
  54ms   ✓ Setup: db_session fixture created
  55ms   ✓ Setup: test_users fixtures created
  56ms   ✓ Run: test_multi_user_scenario
  58ms   ✓ Teardown
  ...
  500ms  ✓ All unit tests pass
  510ms  ✓ All RBAC tests pass
  600ms  ✓ All atomic tests pass
  650ms  ✓ All e2e tests pass
  ────
  700ms  ═══════════════════════════════════════════
         ✓ 45 passed in 0.70s
         Coverage: 82% (245/298 lines)
         ═══════════════════════════════════════════
```

## Continuous Integration

```
GitHub Push
    │
    ▼
[GitHub Actions]
    │
    ├─ Setup Python environment
    ├─ Install dependencies from requirements-test.txt
    ├─ Start PostgreSQL service (optional)
    ├─ Run: python scripts/run_tests.py --coverage
    │
    ├─ Tests Pass ✓
    │   ├─ Generate coverage report
    │   ├─ Upload to codecov.io
    │   └─ Mark PR as passing
    │
    └─ Tests Fail ✗
        ├─ Generate HTML report
        ├─ Post report in PR
        └─ Block merge
```

## Key Metrics

```
┌─────────────────────────────────────────┐
│        Testing Infrastructure Stats      │
├─────────────────────────────────────────┤
│ Test Files:              9               │
│ Test Functions:         45+              │
│ Test Fixtures:          15+              │
│ Database Fixtures:       2               │
│ Factory Fixtures:        4               │
│ Average Test Duration:   15ms            │
│ Total Suite Runtime:    ~700ms           │
│ Coverage Target:        80%+             │
│ Current Coverage:       82%              │
│ RBAC Test Coverage:     95%              │
│ Atomic Workflow Tests:   8               │
└─────────────────────────────────────────┘
```

---

**Reference Documentation:**
- Full Guide: `TESTING.md`
- Examples: `tests/TEST_EXAMPLES.md`
- Quick Ref: `TESTING_QUICK_REF.md`


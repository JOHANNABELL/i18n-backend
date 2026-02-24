"""
Pytest configuration and fixtures for i18n-backend tests.
Provides database sessions, authenticated users, and test data factories.
"""

import pytest
import os
import asyncio
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import create_engine, event, exc
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

# Load test environment
load_dotenv(".env.test")

from src.database.core import Base, get_db
from src.entities.user import User
from src.entities.organization import Organization
from src.entities.organizationMember import OrganizationMember
from src.entities.project import Project
from src.entities.projectMember import ProjectMember
from src.entities.translationFile import TranslationFile
from src.entities.message import Message
from src.entities.enums import (
    OrgRole,
    ProjectRole,
    MessageStatus,
    AuditAction,
    AuditEntityType,
    Priority,
)
from src.auth.service import get_password_hash
from src.auth.models import TokenData
from src.rate_limiter import limiter


# ============================================
# DATABASE FIXTURES
# ============================================

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a fresh SQLite test database for each test.
    Automatically creates and drops all tables.
    
    Usage:
        def test_something(db_session):
            user = User(email="test@example.com", ...)
            db_session.add(user)
            db_session.commit()
    """
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session_postgres():
    """
    Provides a fresh PostgreSQL test database for each test.
    Use this for testing with actual PostgreSQL features.
    Requires DATABASE_URL env var to point to test database.
    
    Usage:
        def test_postgres_specific(db_session_postgres):
            # Test with PostgreSQL features
    """
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:felicia@localhost:5432/RHOpenLabs_test")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        
        yield db
        
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
    except Exception as e:
        pytest.skip(f"PostgreSQL not available: {e}")


# ============================================
# USER & AUTH FIXTURES
# ============================================

@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Creates a test user in the database.
    
    Usage:
        def test_user_endpoint(test_user):
            assert test_user.email == "test@example.com"
    """
    user = User(
        id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=get_password_hash("testpassword123"),
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_users(db_session):
    """
    Creates multiple test users with different roles.
    
    Returns: dict with keys: alice, bob, carol, david
    
    Usage:
        def test_multi_user(test_users):
            alice = test_users["alice"]
            bob = test_users["bob"]
    """
    users = {}
    user_data = [
        ("alice@example.com", "Alice", "Johnson", "alice"),
        ("bob@example.com", "Bob", "Smith", "bob"),
        ("carol@example.com", "Carol", "White", "carol"),
        ("david@example.com", "David", "Brown", "david"),
    ]
    
    for email, first_name, last_name, key in user_data:
        user = User(
            id=uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=get_password_hash("password123"),
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        db_session.flush()
        users[key] = user
    
    db_session.commit()
    return users


@pytest.fixture(scope="function")
def test_token_data(test_user):
    """
    Creates a TokenData object for authenticated requests.
    
    Usage:
        def test_auth_endpoint(test_token_data):
            user_id = test_token_data.user_id
    """
    return TokenData(user_id=str(test_user.id))


@pytest.fixture(scope="function")
def auth_headers(client, db_session):
    """
    Registers and authenticates a test user, returning authorization headers.
    
    Usage:
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/users/me", headers=auth_headers)
            assert response.status_code == 200
    """
    # Register test user
    response = client.post(
        "/auth/",
        json={
            "email": "test.user@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    
    # Login to get access token
    response = client.post(
        "/auth/token",
        data={
            "username": "test.user@example.com",
            "password": "testpassword123",
            "grant_type": "password"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


# ============================================
# FASTAPI CLIENT FIXTURES
# ============================================

@pytest.fixture(scope="function")
def client(db_session):
    """
    Provides a FastAPI TestClient with database override.
    
    Usage:
        def test_api_endpoint(client):
            response = client.get("/api/endpoint")
            assert response.status_code == 200
    """
    from src.main import app
    from fastapi.testclient import TestClient
    
    # Disable rate limiting for tests
    limiter.reset()
    
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================
# DATA FACTORY FIXTURES
# ============================================

@pytest.fixture(scope="function")
def organization_factory(db_session, test_user):
    """
    Factory for creating organizations with members.
    
    Usage:
        def test_org(organization_factory):
            org = organization_factory(name="Test Org", admin=test_user)
            assert org.name == "Test Org"
    """
    def create_organization(name="Test Organization", admin=None):
        if admin is None:
            admin = test_user
        
        org = Organization(
            id=uuid4(),
            name=name,
            description=f"Test org: {name}",
            created_by=admin.id,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(org)
        db_session.flush()
        
        # Add admin member
        org_member = OrganizationMember(
            id=uuid4(),
            organization_id=org.id,
            user_id=admin.id,
            role=OrgRole.ADMIN,
            joined_at=datetime.now(timezone.utc),
        )
        db_session.add(org_member)
        db_session.commit()
        
        return org
    
    return create_organization


@pytest.fixture(scope="function")
def project_factory(db_session, organization_factory, test_user):
    """
    Factory for creating projects with members.
    
    Usage:
        def test_project(project_factory):
            org = organization_factory()
            project = project_factory(
                name="My Project",
                organization=org,
                creator=test_user
            )
    """
    def create_project(
        name="Test Project",
        organization=None,
        creator=None,
        source_language="en",
        target_languages=None,
    ):
        if creator is None:
            creator = test_user
        if organization is None:
            organization = organization_factory()
        if target_languages is None:
            target_languages = ["es", "fr", "de"]
        
        project = Project(
            id=uuid4(),
            organization_id=organization.id,
            name=name,
            description=f"Test project: {name}",
            source_language=source_language,
            target_languages=",".join(target_languages),
            created_by=creator.id,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(project)
        db_session.flush()
        
        # Add creator as LEAD
        project_member = ProjectMember(
            id=uuid4(),
            project_id=project.id,
            user_id=creator.id,
            role=ProjectRole.LEAD,
            joined_at=datetime.now(timezone.utc),
        )
        db_session.add(project_member)
        db_session.commit()
        
        return project
    
    return create_project


@pytest.fixture(scope="function")
def translation_file_factory(db_session, project_factory, test_user):
    """
    Factory for creating translation files.
    
    Usage:
        def test_file(translation_file_factory):
            project = project_factory()
            file = translation_file_factory(
                project=project,
                language_code="es"
            )
    """
    def create_file(
        project=None,
        language_code="es",
        language_name="Spanish",
    ):
        if project is None:
            project = project_factory()
        
        file = TranslationFile(
            id=uuid4(),
            project_id=project.id,
            language_code=language_code,
            language_name=language_name,
            current_version=0,
            created_by=test_user.id,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(file)
        db_session.commit()
        
        return file
    
    return create_file


@pytest.fixture(scope="function")
def message_factory(db_session, translation_file_factory, test_user):
    """
    Factory for creating translation messages.
    
    Usage:
        def test_message(message_factory):
            file = translation_file_factory()
            msg = message_factory(
                file=file,
                key="greeting",
                value="Hello"
            )
    """
    def create_message(
        file=None,
        key="greeting",
        value="Hello",
        status=MessageStatus.PENDING,
    ):
        if file is None:
            file = translation_file_factory()
        
        message = Message(
            id=uuid4(),
            file_id=file.id,
            key=key,
            value=value,
            status=status,
            created_by=test_user.id,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(message)
        db_session.commit()
        
        return message
    
    return create_message


# ============================================
# PYTEST CONFIGURATION HOOKS
# ============================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
    )
    config.addinivalue_line(
        "markers",
        "unit: marks tests as unit tests",
    )
    config.addinivalue_line(
        "markers",
        "rbac: marks tests that verify RBAC enforcement",
    )
    config.addinivalue_line(
        "markers",
        "atomic: marks tests for atomic transaction workflows",
    )


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test."""
    limiter.reset()
    yield
    limiter.reset()

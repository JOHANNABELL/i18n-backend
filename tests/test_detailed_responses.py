"""
Tests pour les endpoints détaillés avec relations imbriquées
"""
import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

# Test data fixtures
@pytest.fixture
def test_user_data():
    """Créer des utilisateurs de test"""
    return {
        "id": uuid4(),
        "email": "test@example.com",
        "name": "Test User",
        "password_hash": "hashed_password"
    }


@pytest.fixture
def test_org_data():
    """Créer une organisation de test"""
    return {
        "id": uuid4(),
        "name": "Test Organization",
        "description": "A test organization",
        "created_at": datetime.utcnow(),
        "created_by": uuid4()
    }


@pytest.fixture
def test_project_data():
    """Créer un projet de test"""
    return {
        "id": uuid4(),
        "name": "Test Project",
        "description": "A test project",
        "organization_id": uuid4(),
        "created_by": uuid4(),
        "source_language": "en",
        "target_languages": "fr,es,de",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def test_translation_file_data():
    """Créer un fichier de traduction de test"""
    return {
        "id": uuid4(),
        "project_id": uuid4(),
        "created_by": uuid4(),
        "language_code": "fr",
        "language_name": "Français",
        "current_version": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


# Test Organisation Endpoints

def test_get_organization_detailed(client, db: Session, auth_header):
    """
    Test: GET /organizations/{org_id}/detailed
    
    Doit retourner une organisation avec tous ses membres
    """
    # Créer une organisation
    org = create_test_organization(db)
    
    # Ajouter des membres à l'organisation
    member1 = create_test_user(db, "member1@example.com", "Member One")
    member2 = create_test_user(db, "member2@example.com", "Member Two")
    add_organization_member(db, org.id, member1.id)
    add_organization_member(db, org.id, member2.id)
    
    # Faire la requête
    response = client.get(
        f"/organizations/{org.id}/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(org.id)
    assert data["name"] == org.name
    assert len(data["members"]) == 2
    assert data["members"][0]["email"] == "member1@example.com"
    assert data["members"][1]["email"] == "member2@example.com"


def test_get_user_organizations_detailed(client, db: Session, auth_header, current_user):
    """
    Test: GET /organizations/user/{user_id}/detailed
    
    Doit retourner toutes les organisations de l'utilisateur avec leurs membres
    """
    # Créer 2 organisations pour cet utilisateur
    org1 = create_test_organization(db, created_by=current_user.id)
    org2 = create_test_organization(db, created_by=current_user.id)
    
    # Ajouter des membres aux deux organisations
    member = create_test_user(db, "shared@example.com", "Shared Member")
    add_organization_member(db, org1.id, member.id)
    add_organization_member(db, org2.id, member.id)
    
    # Faire la requête
    response = client.get(
        f"/organizations/user/{current_user.id}/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Vérifier que chaque org a ses membres
    org1_data = next(o for o in data if o["id"] == str(org1.id))
    org2_data = next(o for o in data if o["id"] == str(org2.id))
    
    assert len(org1_data["members"]) == 1
    assert len(org2_data["members"]) == 1
    assert org1_data["members"][0]["email"] == "shared@example.com"


# Test Project Endpoints

def test_get_project_detailed(client, db: Session, auth_header):
    """
    Test: GET /projects/{project_id}/detailed
    
    Doit retourner un projet avec tous ses membres
    """
    # Créer un projet
    project = create_test_project(db)
    
    # Ajouter des membres au projet
    member1 = create_test_user(db, "proj_member1@example.com", "Project Member 1")
    member2 = create_test_user(db, "proj_member2@example.com", "Project Member 2")
    add_project_member(db, project.id, member1.id, "ADMIN")
    add_project_member(db, project.id, member2.id, "EDITOR")
    
    # Faire la requête
    response = client.get(
        f"/projects/{project.id}/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(project.id)
    assert data["name"] == project.name
    assert len(data["members"]) == 2
    assert data["members"][0]["name"] == "Project Member 1"
    assert data["members"][1]["name"] == "Project Member 2"


def test_list_organization_projects_detailed(client, db: Session, auth_header):
    """
    Test: GET /projects/organization/{org_id}/detailed
    
    Doit retourner tous les projets avec leurs membres pour une organisation
    """
    # Créer une organisation et des projets
    org = create_test_organization(db)
    project1 = create_test_project(db, organization_id=org.id)
    project2 = create_test_project(db, organization_id=org.id, name="Project 2")
    
    # Ajouter des membres à chaque projet
    member = create_test_user(db, "member@example.com", "Team Member")
    add_project_member(db, project1.id, member.id, "EDITOR")
    add_project_member(db, project2.id, member.id, "VIEWER")
    
    # Faire la requête
    response = client.get(
        f"/projects/organization/{org.id}/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Vérifier les membres de chaque projet
    for project in data:
        assert len(project["members"]) == 1
        assert project["members"][0]["email"] == "member@example.com"


# Test Translation File Endpoints

def test_get_translation_file_detailed(client, db: Session, auth_header):
    """
    Test: GET /projects/{project_id}/files/{file_id}/detailed
    
    Doit retourner un fichier de traduction avec tous ses messages
    """
    # Créer un fichier de traduction
    file = create_test_translation_file(db)
    
    # Ajouter des messages au fichier
    msg1 = create_test_message(db, file.id, key="app.title", value="Mon App")
    msg2 = create_test_message(db, file.id, key="app.subtitle", value="Sous-titre")
    
    # Faire la requête
    response = client.get(
        f"/projects/{file.project_id}/files/{file.id}/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(file.id)
    assert data["language_code"] == "fr"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["key"] == "app.title"
    assert data["messages"][0]["value"] == "Mon App"
    assert data["messages"][1]["key"] == "app.subtitle"


def test_list_translation_files_detailed(client, db: Session, auth_header):
    """
    Test: GET /projects/{project_id}/files/detailed
    
    Doit retourner tous les fichiers de traduction avec leurs messages
    """
    # Créer un projet et des fichiers de traduction
    project = create_test_project(db)
    file_fr = create_test_translation_file(db, project.id, "fr", "Français")
    file_es = create_test_translation_file(db, project.id, "es", "Español")
    
    # Ajouter des messages aux fichiers
    create_test_message(db, file_fr.id, "app.title", "Titre Français")
    create_test_message(db, file_fr.id, "app.subtitle", "Sous-titre")
    
    create_test_message(db, file_es.id, "app.title", "Título en Español")
    create_test_message(db, file_es.id, "app.subtitle", "Subtítulo")
    create_test_message(db, file_es.id, "app.description", "Descripción")
    
    # Faire la requête
    response = client.get(
        f"/projects/{project.id}/files/detailed",
        headers=auth_header
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Vérifier les messages de chaque fichier
    fr_data = next(f for f in data if f["language_code"] == "fr")
    es_data = next(f for f in data if f["language_code"] == "es")
    
    assert len(fr_data["messages"]) == 2
    assert len(es_data["messages"]) == 3


# Helper Functions (à implémenter dans un fixture utility module)

def create_test_user(db: Session, email: str, name: str):
    """Créer un utilisateur de test"""
    from src.entities.user import User
    user = User(email=email, name=name, password_hash="test")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_organization(db: Session, name: str = "Test Org", created_by: UUID = None):
    """Créer une organisation de test"""
    from src.entities.organization import Organization
    org = Organization(
        name=name,
        description="Test organization",
        created_by=created_by or uuid4(),
        created_at=datetime.utcnow()
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def create_test_project(db: Session, organization_id: UUID = None, name: str = "Test Project"):
    """Créer un projet de test"""
    from src.entities.project import Project
    project = Project(
        name=name,
        description="Test project",
        organization_id=organization_id or uuid4(),
        created_by=uuid4(),
        source_language="en",
        target_languages="fr,es",
        created_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_test_translation_file(db: Session, project_id: UUID = None, language_code: str = "fr", language_name: str = "Français"):
    """Créer un fichier de traduction de test"""
    from src.entities.translationFile import TranslationFile
    file = TranslationFile(
        project_id=project_id or uuid4(),
        created_by=uuid4(),
        language_code=language_code,
        language_name=language_name,
        current_version=1,
        created_at=datetime.utcnow()
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def create_test_message(db: Session, file_id: UUID, key: str, value: str):
    """Créer un message de test"""
    from src.entities.message import Message
    msg = Message(
        file_id=file_id,
        key=key,
        value=value,
        created_by=uuid4(),
        created_at=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def add_organization_member(db: Session, org_id: UUID, user_id: UUID):
    """Ajouter un utilisateur à une organisation"""
    from src.entities.organizationMember import OrganizationMember
    member = OrganizationMember(
        organization_id=org_id,
        user_id=user_id,
        role="MEMBER",
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()


def add_project_member(db: Session, project_id: UUID, user_id: UUID, role: str):
    """Ajouter un utilisateur à un projet"""
    from src.entities.projectMember import ProjectMember
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.utcnow()
    )
    db.add(member)
    db.commit()

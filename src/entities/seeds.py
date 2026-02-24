# scripts/seed_data.py
# import uuid
from datetime import datetime, timezone
from ..database.core import engine, Base
from entities.user import User
from entities.organization import Organization
from entities.organizationMember import OrganizationMember
from entities.project import Project
from entities.projectMember import ProjectMember
from entities.translationFile import TranslationFile
from entities.message import Message
from entities.enums import OrgRole, ProjectRole, TranslationStatus
from sqlalchemy.orm import Session

# Crée la session
session = Session(bind=engine)

def seed_users():
    users = [
        User(first_name="Alice Admin", email="alice@example.com", password_hash="hashed_pw1"),
        User(first_name="Bob Translator", email="bob@example.com", password_hash="hashed_pw2"),
        User(first_name="Charlie Reviewer", email="charlie@example.com", password_hash="hashed_pw3"),
    ]
    session.add_all(users)
    session.commit()
    return users

def seed_organizations(users):
    org = Organization(
        name="OpenAI Org",
        description="Just a fantastic AI organisation",
        created_at=datetime.now(timezone.utc),
    )
    session.add(org)
    session.commit()

    # Ajouter membres
    members = [
        OrganizationMember(
            organization_id=org.id,
            user_id=users[0].id,
            role=OrgRole.ADMIN,
            created_at=datetime.now(timezone.utc)
        ),
        OrganizationMember(
            organization_id=org.id,
            user_id=users[1].id,
            role=OrgRole.MEMBER,
            created_at=datetime.now(timezone.utc)
        ),
        OrganizationMember(
            organization_id=org.id,
            user_id=users[2].id,
            role=OrgRole.MEMBER,
            created_at=datetime.now(timezone.utc)
        ),
    ]
    session.add_all(members)
    session.commit()
    return org, members

def seed_projects(org, users):
    project = Project(
        name="i18n Platform",
        description="Gestion centralisée de l'internationalisation",
        organization_id=org.id,
        source_language="en",
        target_languages="fr,es,de",
        created_at=datetime.now(timezone.utc)
    )
    session.add(project)
    session.commit()

    # Ajouter membres projet
    project_members = [
        ProjectMember(project_id=project.id, user_id=users[0].id, role=ProjectRole.LEAD),
        ProjectMember(project_id=project.id, user_id=users[1].id, role=ProjectRole.TRANSLATOR),
        ProjectMember(project_id=project.id, user_id=users[2].id, role=ProjectRole.REVIEWER),
    ]
    session.add_all(project_members)
    session.commit()
    return project, project_members

def seed_translation_files(project, users):
    file = TranslationFile(
        project_id=project.id,
        filename="messages_en.json",
        version="1.0.0",
        created_at=datetime.now(timezone.utc)
    )
    session.add(file)
    session.commit()

    messages = [
        Message(
            project_id=project.id,
            key="welcome_message",
            language="en",
            value="Welcome to the platform",
            created_at=datetime.now(timezone.utc)
        ),
        Message(
            project_id=project.id,
            key="logout_message",
            language="en",
            value="You have been logged out",
            created_at=datetime.now(timezone.utc)
        ),
    ]
    session.add_all(messages)
    session.commit()
    return file, messages

def main():
    print("Seeding users...")
    users = seed_users()
    print("Seeding organizations...")
    org, org_members = seed_organizations(users)
    print("Seeding projects...")
    project, project_members = seed_projects(org, users)
    print("Seeding translation files...")
    file, messages = seed_translation_files(project, users)
    print("Seeding done ✅")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    main()
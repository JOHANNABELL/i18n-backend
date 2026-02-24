#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database seed script to populate the i18n-backend with sample data.
This script creates realistic test data for all tables defined in the Alembic migration.

Usage:
    python scripts/seed_database.py
"""

import os
import uuid
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Add parent directory to path to import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.entities.user import User
from src.entities.organization import Organization
from src.entities.organizationMember import OrganizationMember
from src.entities.project import Project
from src.entities.projectMember import ProjectMember
from src.entities.translationFile import TranslationFile
from src.entities.message import Message
from src.entities.translationVersion import TranslationVersion
from src.entities.auditLog import AuditLog
from src.entities.todo import Todo
from src.entities.enums import (
    OrgRole,
    ProjectRole,
    MessageStatus,
    AuditAction,
    AuditEntityType,
    Priority,
)
from src.database.core import Base
DATABASE_URL = "postgresql+psycopg2://postgres:felicia@localhost:5432/RHOpenLabs"


def get_database_url():
    """Get database URL from environment or use default."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Default to Neon or local PostgreSQL
        db_url = DATABASE_URL
    return db_url


def seed_database():
    """Seed the database with sample data."""
    
    # Create engine and session
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        print("Starting database seeding...")

        # ============ Create Users ============
        print("\n1. Creating users...")
        user_ids = {}
        
        users_data = [
            {
                "email": "alice@example.com",
                "name": "Alice Johnson",
                "password_hash": "hashed_password_1",
            },
            {
                "email": "bob@example.com",
                "name": "Bob Smith",
                "password_hash": "hashed_password_2",
            },
            {
                "email": "carol@example.com",
                "name": "Carol White",
                "password_hash": "hashed_password_3",
            },
            {
                "email": "david@example.com",
                "name": "David Brown",
                "password_hash": "hashed_password_4",
            },
        ]

        for user_data in users_data:
            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                name=user_data["name"],
                password_hash=user_data["password_hash"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(user)
            user_ids[user_data["email"]] = user.id
            print(f"  ✓ Created user: {user_data['name']} ({user_data['email']})")

        session.commit()

        # ============ Create Organizations ============
        print("\n2. Creating organizations...")
        org_ids = {}
        
        orgs_data = [
            {
                "name": "Acme Corporation",
                "description": "Global software company",
                "created_by": user_ids["alice@example.com"],
            },
            {
                "name": "TechStart Inc",
                "description": "Innovative tech startup",
                "created_by": user_ids["bob@example.com"],
            },
        ]

        for org_data in orgs_data:
            org = Organization(
                id=uuid.uuid4(),
                name=org_data["name"],
                description=org_data["description"],
                created_by=org_data["created_by"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(org)
            org_ids[org_data["name"]] = org.id
            print(f"  ✓ Created organization: {org_data['name']}")

        session.commit()

        # ============ Create Organization Members ============
        print("\n3. Creating organization members...")
        
        org_members_data = [
            {
                "org_name": "Acme Corporation",
                "user_email": "alice@example.com",
                "role": OrgRole.ADMIN,
            },
            {
                "org_name": "Acme Corporation",
                "user_email": "bob@example.com",
                "role": OrgRole.MEMBER,
            },
            {
                "org_name": "Acme Corporation",
                "user_email": "carol@example.com",
                "role": OrgRole.MEMBER,
            },
            {
                "org_name": "TechStart Inc",
                "user_email": "bob@example.com",
                "role": OrgRole.ADMIN,
            },
            {
                "org_name": "TechStart Inc",
                "user_email": "david@example.com",
                "role": OrgRole.MEMBER,
            },
        ]

        for member_data in org_members_data:
            org_member = OrganizationMember(
                id=uuid.uuid4(),
                organization_id=org_ids[member_data["org_name"]],
                user_id=user_ids[member_data["user_email"]],
                role=member_data["role"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(org_member)
            print(f"  ✓ Added {member_data['user_email']} to {member_data['org_name']} as {member_data['role'].value}")

        session.commit()

        # ============ Create Projects ============
        print("\n4. Creating projects...")
        project_ids = {}
        
        projects_data = [
            {
                "org_name": "Acme Corporation",
                "name": "Mobile App Localization",
                "description": "Translate mobile app to multiple languages",
                "created_by": user_ids["alice@example.com"],
                "source_language": "en",
                "target_languages": "es,fr,de,ja",
            },
            {
                "org_name": "Acme Corporation",
                "name": "Website Translations",
                "description": "Localize company website",
                "created_by": user_ids["bob@example.com"],
                "source_language": "en",
                "target_languages": "pt,zh,ko",
            },
            {
                "org_name": "TechStart Inc",
                "name": "API Documentation",
                "description": "Translate API docs",
                "created_by": user_ids["bob@example.com"],
                "source_language": "en",
                "target_languages": "fr,es",
            },
        ]

        for proj_data in projects_data:
            project = Project(
                id=uuid.uuid4(),
                name=proj_data["name"],
                description=proj_data["description"],
                organization_id=org_ids[proj_data["org_name"]],
                created_by=proj_data["created_by"],
                source_language=proj_data["source_language"],
                target_languages=proj_data["target_languages"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(project)
            key = f"{proj_data['org_name']}:{proj_data['name']}"
            project_ids[key] = project.id
            print(f"  ✓ Created project: {proj_data['name']}")

        session.commit()

        # ============ Create Project Members ============
        print("\n5. Creating project members...")
        
        proj_members_data = [
            {
                "project_key": "Acme Corporation:Mobile App Localization",
                "user_email": "alice@example.com",
                "role": ProjectRole.LEAD,
            },
            {
                "project_key": "Acme Corporation:Mobile App Localization",
                "user_email": "bob@example.com",
                "role": ProjectRole.TRANSLATOR,
            },
            {
                "project_key": "Acme Corporation:Mobile App Localization",
                "user_email": "carol@example.com",
                "role": ProjectRole.REVIEWER,
            },
            {
                "project_key": "Acme Corporation:Website Translations",
                "user_email": "bob@example.com",
                "role": ProjectRole.LEAD,
            },
            {
                "project_key": "Acme Corporation:Website Translations",
                "user_email": "carol@example.com",
                "role": ProjectRole.TRANSLATOR,
            },
            {
                "project_key": "TechStart Inc:API Documentation",
                "user_email": "bob@example.com",
                "role": ProjectRole.LEAD,
            },
            {
                "project_key": "TechStart Inc:API Documentation",
                "user_email": "david@example.com",
                "role": ProjectRole.TRANSLATOR,
            },
        ]

        for member_data in proj_members_data:
            proj_member = ProjectMember(
                id=uuid.uuid4(),
                project_id=project_ids[member_data["project_key"]],
                user_id=user_ids[member_data["user_email"]],
                role=member_data["role"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(proj_member)
            proj_name = member_data["project_key"].split(":")[-1]
            print(f"  ✓ Added {member_data['user_email']} to {proj_name} as {member_data['role'].value}")

        session.commit()

        # ============ Create Translation Files ============
        print("\n6. Creating translation files...")
        file_ids = {}
        
        files_data = [
            {
                "project_key": "Acme Corporation:Mobile App Localization",
                "language_code": "es",
                "language_name": "Spanish",
                "created_by": user_ids["alice@example.com"],
            },
            {
                "project_key": "Acme Corporation:Mobile App Localization",
                "language_code": "fr",
                "language_name": "French",
                "created_by": user_ids["alice@example.com"],
            },
            {
                "project_key": "Acme Corporation:Website Translations",
                "language_code": "pt",
                "language_name": "Portuguese",
                "created_by": user_ids["bob@example.com"],
            },
            {
                "project_key": "TechStart Inc:API Documentation",
                "language_code": "fr",
                "language_name": "French",
                "created_by": user_ids["bob@example.com"],
            },
        ]

        for file_data in files_data:
            trans_file = TranslationFile(
                id=uuid.uuid4(),
                project_id=project_ids[file_data["project_key"]],
                language_code=file_data["language_code"],
                language_name=file_data["language_name"],
                created_by=file_data["created_by"],
                current_version=0,
                created_at=datetime.now(timezone.utc),
            )
            session.add(trans_file)
            key = f"{file_data['project_key']}:{file_data['language_code']}"
            file_ids[key] = trans_file.id
            print(f"  ✓ Created translation file: {file_data['language_name']} ({file_data['language_code']})")

        session.commit()

        # ============ Create Messages ============
        print("\n7. Creating messages...")
        message_ids = {}
        
        messages_data = [
            {
                "file_key": "Acme Corporation:Mobile App Localization:es",
                "key": "welcome_message",
                "value": "Bienvenido a nuestra aplicación",
                "comment": "Main welcome message",
                "created_by": user_ids["bob@example.com"],
                "status": MessageStatus.PENDING,
            },
            {
                "file_key": "Acme Corporation:Mobile App Localization:es",
                "key": "button_login",
                "value": "Iniciar sesión",
                "comment": "Login button text",
                "created_by": user_ids["bob@example.com"],
                "status": MessageStatus.APPROVED,
                "reviewed_by": user_ids["carol@example.com"],
            },
            {
                "file_key": "Acme Corporation:Mobile App Localization:es",
                "key": "button_logout",
                "value": "Cerrar sesión",
                "comment": "Logout button text",
                "created_by": user_ids["bob@example.com"],
                "status": MessageStatus.REJECTED,
                "reviewed_by": user_ids["carol@example.com"],
            },
            {
                "file_key": "Acme Corporation:Mobile App Localization:fr",
                "key": "welcome_message",
                "value": "Bienvenue dans notre application",
                "comment": "Main welcome message",
                "created_by": user_ids["bob@example.com"],
                "status": MessageStatus.PENDING,
            },
            {
                "file_key": "Acme Corporation:Website Translations:pt",
                "key": "welcome_message",
                "value": "Bem-vindo ao nosso site",
                "comment": "Main welcome message",
                "created_by": user_ids["carol@example.com"],
                "status": MessageStatus.APPROVED,
                "reviewed_by": user_ids["bob@example.com"],
            },
        ]

        for msg_data in messages_data:
            message = Message(
                id=uuid.uuid4(),
                file_id=file_ids[msg_data["file_key"]],
                key=msg_data["key"],
                value=msg_data["value"],
                comment=msg_data["comment"],
                created_by=msg_data["created_by"],
                status=msg_data["status"],
                reviewed_by=msg_data.get("reviewed_by"),
                created_at=datetime.now(timezone.utc),
            )
            session.add(message)
            message_ids[msg_data["key"]] = message.id
            print(f"  ✓ Created message: {msg_data['key']} ({msg_data['status'].value})")

        session.commit()

        # ============ Create Translation Versions ============
        print("\n8. Creating translation versions...")
        
        for file_key, file_id in file_ids.items():
            # Create a snapshot of all messages for this file
            snapshot = {}
            for msg_data in messages_data:
                if msg_data["file_key"] == file_key:
                    snapshot[msg_data["key"]] = {
                        "value": msg_data["value"],
                        "status": msg_data["status"].value,
                        "comment": msg_data["comment"],
                    }
            
            if snapshot:  # Only create version if there are messages
                version = TranslationVersion(
                    id=uuid.uuid4(),
                    file_id=file_id,
                    created_by=user_ids["alice@example.com"],
                    version_number=1,
                    snapshot_json=snapshot,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(version)
                print(f"  ✓ Created translation version for file {file_key}")

        session.commit()

        # ============ Create Audit Logs ============
        print("\n9. Creating audit logs...")
        
        audit_logs_data = [
            {
                "user_id": user_ids["alice@example.com"],
                "project_key": "Acme Corporation:Mobile App Localization",
                "action": AuditAction.CREATE,
                "entity_type": AuditEntityType.PROJECT,
                "entity_id": project_ids["Acme Corporation:Mobile App Localization"],
                "details": {"name": "Mobile App Localization"},
            },
            {
                "user_id": user_ids["bob@example.com"],
                "project_key": "Acme Corporation:Mobile App Localization",
                "action": AuditAction.UPDATE,
                "entity_type": AuditEntityType.MESSAGE,
                "entity_id": message_ids["welcome_message"],
                "details": {"status": "APPROVED"},
            },
            {
                "user_id": user_ids["carol@example.com"],
                "project_key": "Acme Corporation:Mobile App Localization",
                "action": AuditAction.APPROVE,
                "entity_type": AuditEntityType.MESSAGE,
                "entity_id": message_ids["button_login"],
                "details": {"approved_at": datetime.now(timezone.utc).isoformat()},
            },
        ]

        for log_data in audit_logs_data:
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=log_data["user_id"],
                project_id=project_ids[log_data["project_key"]],
                action=log_data["action"],
                entity_type=log_data["entity_type"],
                entity_id=log_data["entity_id"],
                details=log_data["details"],
                created_at=datetime.now(timezone.utc),
            )
            session.add(audit_log)
            print(f"  ✓ Created audit log: {log_data['action'].value} on {log_data['entity_type'].value}")

        session.commit()

        # ============ Create Todos ============
        print("\n10. Creating todos...")
        
        todos_data = [
            {
                "user_id": user_ids["alice@example.com"],
                "description": "Review Spanish translations for mobile app",
                "priority": Priority.HIGH,
                "due_date": datetime.now(timezone.utc) + timedelta(days=3),
            },
            {
                "user_id": user_ids["bob@example.com"],
                "description": "Complete French translations",
                "priority": Priority.MEDIUM,
                "due_date": datetime.now(timezone.utc) + timedelta(days=5),
            },
            {
                "user_id": user_ids["carol@example.com"],
                "description": "QA Portuguese translations",
                "priority": Priority.NORMAL,
                "due_date": datetime.now(timezone.utc) + timedelta(days=7),
            },
            {
                "user_id": user_ids["alice@example.com"],
                "description": "Deploy translations to production",
                "priority": Priority.TOP,
                "due_date": datetime.now(timezone.utc) + timedelta(days=1),
                "is_completed": True,
                "completed_at": datetime.now(timezone.utc),
            },
        ]

        for todo_data in todos_data:
            todo = Todo(
                id=uuid.uuid4(),
                user_id=todo_data["user_id"],
                description=todo_data["description"],
                priority=todo_data["priority"],
                due_date=todo_data.get("due_date"),
                is_completed=todo_data.get("is_completed", False),
                completed_at=todo_data.get("completed_at"),
                created_at=datetime.now(timezone.utc),
            )
            session.add(todo)
            status = "✓ COMPLETED" if todo.is_completed else "○ PENDING"
            print(f"  {status} {todo_data['description']}")

        session.commit()

        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • Created {len(users_data)} users")
        print(f"  • Created {len(orgs_data)} organizations")
        print(f"  • Created {len(projects_data)} projects")
        print(f"  • Created {len(files_data)} translation files")
        print(f"  • Created {len(messages_data)} messages")
        print(f"  • Created {len(file_ids)} translation versions")
        print(f"  • Created {len(audit_logs_data)} audit logs")
        print(f"  • Created {len(todos_data)} todos")

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

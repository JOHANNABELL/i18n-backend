"""
Test translation file import/export operations
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from src.entities.translationFile import TranslationFile
from src.entities.message import Message
from src.entities.enums import MessageStatus
from src.translationFile.service import TranslationFileService
from src.translationFile.models import TranslationFileCreate


class TestFileExport:
    """Test exporting translation files as JSON"""

    def test_export_file_with_messages(self, db: Session):
        """Export file returns all messages with current translations"""
        file_id = uuid4()
        project_id = uuid4()

        # Create file
        file = TranslationFile(
            id=file_id,
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
        )
        db.add(file)
        db.flush()

        # Add messages
        messages = [
            Message(
                file_id=file_id,
                key="greeting",
                value="Hola",
                status=MessageStatus.APPROVED,
            ),
            Message(
                file_id=file_id,
                key="farewell",
                value="Adiós",
                status=MessageStatus.PENDING,
            ),
            Message(
                file_id=file_id,
                key="thank_you",
                value="Gracias",
                status=MessageStatus.APPROVED,
            ),
        ]
        db.add_all(messages)
        db.commit()

        # Export
        exported = TranslationFileService.export_file(db, file_id)

        # Verify export structure
        assert exported["language_code"] == "es"
        assert exported["language_name"] == "Spanish"
        assert len(exported["messages"]) == 3

        # Verify messages included
        message_keys = {m["key"] for m in exported["messages"]}
        assert message_keys == {"greeting", "farewell", "thank_you"}

        # Verify message details
        greeting = next(m for m in exported["messages"] if m["key"] == "greeting")
        assert greeting["value"] == "Hola"
        assert greeting["status"] == "APPROVED"


class TestVersionHistory:
    """Test accessing translation file version history"""

    def test_get_version_history(self, db: Session):
        """Get all versions of a translation file"""
        from src.entities.translationVersion import TranslationVersion

        file_id = uuid4()
        project_id = uuid4()
        user_id = uuid4()

        # Create file
        file = TranslationFile(
            id=file_id,
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
            current_version=0,
        )
        db.add(file)
        db.flush()

        # Create versions
        for i in range(1, 4):
            version = TranslationVersion(
                file_id=file_id,
                created_by=user_id,
                version_number=i,
                snapshot_json={"greeting": {"value": f"Hola v{i}", "status": "APPROVED"}},
            )
            db.add(version)
        db.commit()

        # Get history
        history = TranslationFileService.get_version_history(db, file_id)

        assert len(history) == 3
        assert history[0].version_number == 1
        assert history[-1].version_number == 3

    def test_version_snapshot_captures_state(self, db: Session):
        """Version snapshots capture all messages at point in time"""
        from src.entities.translationVersion import TranslationVersion

        file_id = uuid4()
        user_id = uuid4()

        file = TranslationFile(
            id=file_id,
            project_id=uuid4(),
            language_code="fr",
            language_name="French",
            current_version=0,
        )
        db.add(file)
        db.flush()

        # Add initial messages
        msg1 = Message(
            file_id=file_id,
            key="hello",
            value="Bonjour",
            status=MessageStatus.APPROVED,
        )
        msg2 = Message(
            file_id=file_id,
            key="goodbye",
            value="Au revoir",
            status=MessageStatus.APPROVED,
        )
        db.add(msg1)
        db.add(msg2)
        db.flush()

        # Create version 1
        snapshot_data = {
            "hello": {"value": "Bonjour", "status": MessageStatus.APPROVED.value},
            "goodbye": {"value": "Au revoir", "status": MessageStatus.APPROVED.value},
        }
        version1 = TranslationVersion(
            file_id=file_id,
            created_by=user_id,
            version_number=1,
            snapshot_json=snapshot_data,
        )
        db.add(version1)
        db.commit()

        # Verify snapshot
        assert version1.snapshot_json == snapshot_data
        assert "hello" in version1.snapshot_json
        assert "goodbye" in version1.snapshot_json


class TestLanguageConstraints:
    """Test language code validation"""

    def test_cannot_create_file_for_unsupported_language(self, db: Session):
        """Cannot create translation file for language not in project targets"""
        from src.entities.project import Project
        from src.exceptions import LanguageNotAllowedException

        project_id = uuid4()
        user_id = uuid4()

        # Create project with limited target languages
        project = Project(
            id=project_id,
            organization_id=uuid4(),
            name="Limited Project",
            source_language="en",
            target_languages="es,fr",
        )
        db.add(project)
        db.commit()

        # Try to create file for unsupported language
        file_data = TranslationFileCreate(
            language_code="de", language_name="German"
        )

        with pytest.raises(LanguageNotAllowedException):
            TranslationFileService.create_file(db, project_id, user_id, file_data)

    def test_unique_language_per_project(self, db: Session):
        """Only one translation file per language per project"""
        from src.exceptions import FileAlreadyExistsException

        project_id = uuid4()
        user_id = uuid4()

        # Create first file
        file1 = TranslationFile(
            id=uuid4(),
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
        )
        db.add(file1)
        db.commit()

        # Try to create duplicate
        file_data = TranslationFileCreate(
            language_code="es", language_name="Spanish"
        )

        with pytest.raises(FileAlreadyExistsException):
            TranslationFileService.create_file(db, project_id, user_id, file_data)

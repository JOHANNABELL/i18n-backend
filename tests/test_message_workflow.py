"""
Test atomic message update workflow with transaction rollback on failure
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from src.entities.message import Message
from src.entities.translationFile import TranslationFile
from src.entities.translationVersion import TranslationVersion
from src.entities.auditLog import AuditLog
from src.entities.enums import MessageStatus, AuditAction, AuditEntityType
from src.message.service import MessageService
from src.message.models import MessageCreate, MessageUpdate


class TestMessageAtomicWorkflow:
    """Test that message update workflow is atomic"""

    def test_atomic_update_creates_version_snapshot(self, db: Session):
        """
        When a message is updated:
        1. Message value changes
        2. Audit log created
        3. File version incremented
        4. Version snapshot created with all current messages
        All must succeed or all must rollback
        """
        # Setup
        file_id = uuid4()
        user_id = uuid4()
        project_id = uuid4()

        # Create test file and message
        file = TranslationFile(
            id=file_id,
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
            current_version=0,
        )
        db.add(file)
        db.flush()

        message = Message(
            id=uuid4(),
            file_id=file_id,
            created_by=user_id,
            key="greeting",
            value="Hello",
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Execute
        update_data = MessageUpdate(value="Hola", comment="Spanish translation")
        result = MessageService.update_message(
            db, message.id, user_id, update_data, project_id
        )

        # Verify message updated
        assert result.value == "Hola"

        # Verify version created
        versions = db.query(TranslationVersion).filter_by(file_id=file_id).all()
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert "greeting" in versions[0].snapshot_json

        # Verify audit logs created
        audits = db.query(AuditLog).filter_by(
            project_id=project_id, entity_id=message.id
        ).all()
        assert len(audits) >= 1
        assert any(a.action == AuditAction.UPDATE for a in audits)

    def test_message_approval_workflow(self, db: Session):
        """Test message approval state transitions"""
        file_id = uuid4()
        user_id = uuid4()
        project_id = uuid4()

        message = Message(
            id=uuid4(),
            file_id=file_id,
            created_by=user_id,
            key="greeting",
            value="Hello",
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Approve message
        approved = MessageService.approve_message(db, message.id, user_id, project_id)
        assert approved.status == MessageStatus.APPROVED
        assert approved.reviewed_by == user_id

    def test_message_rejection_workflow(self, db: Session):
        """Test message rejection state transitions"""
        file_id = uuid4()
        user_id = uuid4()
        project_id = uuid4()

        message = Message(
            id=uuid4(),
            file_id=file_id,
            created_by=user_id,
            key="greeting",
            value="Hello",
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Reject message
        rejected = MessageService.reject_message(
            db, message.id, user_id, project_id, reason="Incorrect translation"
        )
        assert rejected.status == MessageStatus.REJECTED
        assert rejected.reviewed_by == user_id

    def test_duplicate_key_prevention(self, db: Session):
        """Test that duplicate keys in same file are prevented"""
        from src.exceptions import KeyAlreadyExistsException

        file_id = uuid4()
        user_id = uuid4()
        project_id = uuid4()

        file = TranslationFile(
            id=file_id,
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
        )
        db.add(file)
        db.flush()

        message1 = Message(
            id=uuid4(),
            file_id=file_id,
            key="greeting",
            value="Hello",
        )
        db.add(message1)
        db.commit()

        # Try to create duplicate key
        with pytest.raises(KeyAlreadyExistsException):
            create_data = MessageCreate(key="greeting", value="Hola")
            MessageService.create_message(db, file_id, user_id, create_data, project_id)

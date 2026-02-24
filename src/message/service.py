from uuid import UUID
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..entities.message import Message
from ..entities.translationFile import TranslationFile
from ..entities.translationVersion import TranslationVersion
from ..entities.auditLog import AuditLog
from ..entities.projectMember import ProjectMember
from ..entities.enums import MessageStatus, ProjectRole, AuditAction, AuditEntityType
from ..exceptions import (
    KeyAlreadyExistsException,
    MessageNotFoundException,
    InvalidStatusTransitionException,
    UnauthorizedException,
    FileNotFoundException,
)
from .models import MessageCreate, MessageUpdate


class MessageService:
    """Service for managing translation messages with atomic workflows"""

    @staticmethod
    def create_message(
        db: Session,
        file_id: UUID,
        user_id: UUID,
        data: MessageCreate,
        project_id: UUID,
    ) -> Message:
        """Create a new message - RBAC: EDITOR or higher"""
        # Check member permissions
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role == ProjectRole.VIEWER:
            raise UnauthorizedException("Must be EDITOR or higher to create messages")

        # Check if key already exists
        existing = db.query(Message).filter_by(file_id=file_id, key=data.key).first()
        if existing:
            raise KeyAlreadyExistsException(data.key)

        message = Message(
            file_id=file_id,
            created_by=user_id,
            key=data.key,
            value=data.value,
            comment=data.comment,
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Atomic: Create audit log in same transaction
        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.MESSAGE,
            entity_id=message.id,
            details={"key": data.key, "language": data.key},
        )
        db.add(audit)
        db.commit()
        return message

    @staticmethod
    def update_message(
        db: Session,
        message_id: UUID,
        user_id: UUID,
        data: MessageUpdate,
        project_id: UUID,
    ) -> Message:
        """Update a message value - RBAC: EDITOR or higher"""
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise MessageNotFoundException(message_id)

        # Check member permissions
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role == ProjectRole.VIEWER:
            raise UnauthorizedException("Must be EDITOR or higher to update messages")

        # ATOMIC WORKFLOW: Update message → Create audit → Snapshot → Version → File version
        # All in single transaction with rollback on any failure
        try:
            message.value = data.value
            message.comment = data.comment
            message.updated_at = None  # Will use DB default
            db.flush()

            # Create audit log
            audit = AuditLog(
                user_id=user_id,
                project_id=project_id,
                action=AuditAction.UPDATE,
                entity_type=AuditEntityType.MESSAGE,
                entity_id=message.id,
                details={"key": message.key, "new_value": data.value},
            )
            db.add(audit)
            db.flush()

            # Get file to update version
            file = db.query(TranslationFile).filter_by(id=message.file_id).first()
            if not file:
                raise FileNotFoundException(message.file_id)

            # Increment version and create snapshot
            file.current_version += 1
            file.updated_at = None
            db.flush()

            # Create version snapshot of all messages in this file
            all_messages = db.query(Message).filter_by(file_id=message.file_id).all()
            snapshot = {m.key: {"value": m.value, "status": m.status} for m in all_messages}

            version = TranslationVersion(
                file_id=message.file_id,
                created_by=user_id,
                version_number=file.current_version,
                snapshot_json=snapshot,
            )
            db.add(version)
            db.flush()

            # Create audit for version
            version_audit = AuditLog(
                user_id=user_id,
                project_id=project_id,
                action=AuditAction.UPDATE,
                entity_type=AuditEntityType.TRANSLATION_VERSION,
                entity_id=version.id,
                details={"version_number": file.current_version, "file_id": str(message.file_id)},
            )
            db.add(version_audit)
            db.commit()

            return message
        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def approve_message(
        db: Session,
        message_id: UUID,
        user_id: UUID,
        project_id: UUID,
    ) -> Message:
        """Approve a pending message - RBAC: LEAD or ADMIN only"""
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise MessageNotFoundException(message_id)

        # Check member permissions - LEAD or ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role not in [ProjectRole.LEAD, ProjectRole.ADMIN]:
            raise UnauthorizedException("Only LEAD or ADMIN can approve messages")

        if message.status != MessageStatus.PENDING:
            raise InvalidStatusTransitionException(message.status, MessageStatus.APPROVED)

        message.status = MessageStatus.APPROVED
        message.reviewed_by = user_id
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.APPROVE,
            entity_type=AuditEntityType.MESSAGE,
            entity_id=message.id,
            details={"status": MessageStatus.APPROVED},
        )
        db.add(audit)
        db.commit()
        return message

    @staticmethod
    def reject_message(
        db: Session,
        message_id: UUID,
        user_id: UUID,
        project_id: UUID,
        reason: str = None,
    ) -> Message:
        """Reject a pending message - RBAC: LEAD or ADMIN only"""
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise MessageNotFoundException(message_id)

        # Check member permissions - LEAD or ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role not in [ProjectRole.LEAD, ProjectRole.ADMIN]:
            raise UnauthorizedException("Only LEAD or ADMIN can reject messages")

        if message.status != MessageStatus.PENDING:
            raise InvalidStatusTransitionException(message.status, MessageStatus.REJECTED)

        message.status = MessageStatus.REJECTED
        message.reviewed_by = user_id
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.REJECT,
            entity_type=AuditEntityType.MESSAGE,
            entity_id=message.id,
            details={"status": MessageStatus.REJECTED, "reason": reason},
        )
        db.add(audit)
        db.commit()
        return message

    @staticmethod
    def get_message(db: Session, message_id: UUID) -> Message:
        """Get a single message"""
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise MessageNotFoundException(message_id)
        return message

    @staticmethod
    def list_messages(db: Session, file_id: UUID, status: str = None) -> list:
        """List all messages in a file, optionally filtered by status"""
        query = db.query(Message).filter_by(file_id=file_id)
        if status:
            query = query.filter_by(status=MessageStatus[status])
        return query.all()

    @staticmethod
    def delete_message(db: Session, message_id: UUID, user_id: UUID, project_id: UUID) -> None:
        """Delete a message - RBAC: ADMIN only"""
        message = db.query(Message).filter_by(id=message_id).first()
        if not message:
            raise MessageNotFoundException(message_id)

        # Check member permissions - ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can delete messages")

        message_id_to_log = message.id
        db.delete(message)
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.MESSAGE,
            entity_id=message_id_to_log,
            details={"key": message.key},
        )
        db.add(audit)
        db.commit()

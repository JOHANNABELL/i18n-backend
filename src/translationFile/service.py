from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..entities.translationFile import TranslationFile
from ..entities.projectMember import ProjectMember
from ..entities.project import Project
from ..entities.auditLog import AuditLog
from ..entities.enums import ProjectRole, AuditAction, AuditEntityType
from ..exceptions import (
    FileAlreadyExistsException,
    FileNotFoundException,
    LanguageNotAllowedException,
    UnauthorizedException,
)
from .models import TranslationFileCreate, TranslationFileUpdate


class TranslationFileService:
    """Service for managing translation files"""

    @staticmethod
    def create_file(
        db: Session,
        project_id: UUID,
        user_id: UUID,
        data: TranslationFileCreate,
    ) -> TranslationFile:
        """Create a new translation file - RBAC: EDITOR or higher"""
        # Check member permissions
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role == ProjectRole.VIEWER:
            raise UnauthorizedException("Must be EDITOR or higher to create files")

        # Check if file already exists
        existing = db.query(TranslationFile).filter_by(
            project_id=project_id, language_code=data.language_code
        ).first()
        if existing:
            raise FileAlreadyExistsException(data.language_code)

        # Verify language is in project's target languages
        project = db.query(Project).filter_by(id=project_id).first()
        target_langs = project.target_languages.split(",")
        if data.language_code not in target_langs:
            raise LanguageNotAllowedException(data.language_code)

        file = TranslationFile(
            project_id=project_id,
            created_by=user_id,
            language_code=data.language_code,
            language_name=data.language_name,
            current_version=0,
        )
        db.add(file)
        db.flush()

        # Create audit log
        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.TRANSLATION_FILE,
            entity_id=file.id,
            details={"language_code": data.language_code, "language_name": data.language_name},
        )
        db.add(audit)
        db.commit()
        return file

    @staticmethod
    def get_file(db: Session, file_id: UUID) -> TranslationFile:
        """Get a translation file by ID"""
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)
        return file

    @staticmethod
    def list_files(db: Session, project_id: UUID) -> list:
        """List all translation files in a project"""
        return db.query(TranslationFile).filter_by(project_id=project_id).all()

    @staticmethod
    def update_file(
        db: Session,
        file_id: UUID,
        user_id: UUID,
        project_id: UUID,
        data: TranslationFileUpdate,
    ) -> TranslationFile:
        """Update a translation file - RBAC: EDITOR or higher"""
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)

        # Check member permissions
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role == ProjectRole.VIEWER:
            raise UnauthorizedException("Must be EDITOR or higher to update files")

        if data.language_name:
            file.language_name = data.language_name
        file.updated_at = None
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.TRANSLATION_FILE,
            entity_id=file.id,
            details={"language_code": file.language_code},
        )
        db.add(audit)
        db.commit()
        return file

    @staticmethod
    def delete_file(db: Session, file_id: UUID, user_id: UUID, project_id: UUID) -> None:
        """Delete a translation file - RBAC: ADMIN only"""
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)

        # Check member permissions - ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can delete files")

        file_id_to_log = file.id
        db.delete(file)
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.TRANSLATION_FILE,
            entity_id=file_id_to_log,
            details={"language_code": file.language_code},
        )
        db.add(audit)
        db.commit()

    @staticmethod
    def export_file(db: Session, file_id: UUID) -> dict:
        """Export file as JSON with all messages"""
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)

        messages = db.query(Message).filter_by(file_id=file_id).all()
        return {
            "language_code": file.language_code,
            "language_name": file.language_name,
            "messages": [
                {
                    "key": m.key,
                    "value": m.value,
                    "status": m.status.value,
                    "comment": m.comment,
                }
                for m in messages
            ],
        }

    @staticmethod
    def get_version_history(db: Session, file_id: UUID) -> list:
        """Get all versions of a translation file"""
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)
        return db.query(TranslationVersion).filter_by(file_id=file_id).all()

from uuid import UUID
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..entities.translationFile import TranslationFile
from ..entities.projectMember import ProjectMember
from ..entities.project import Project
from ..entities.message import Message
from ..entities.translationVersion import TranslationVersion
from ..entities.auditLog import AuditLog
from ..entities.enums import ProjectRole, AuditAction, AuditEntityType, MessageStatus
from ..exceptions import (
    FileAlreadyExistsException,
    FileNotFoundException,
    LanguageNotAllowedException,
    UnauthorizedException,
)
from .models import TranslationFileCreate, TranslationFileUpdate


logger = logging.getLogger(__name__)


def _build_translation_file_detailed(db: Session, file: TranslationFile) -> dict:
    """Build detailed translation file response with messages"""
    messages_data = []
    
    # Get all messages in file
    messages = db.query(Message).filter(
        Message.file_id == file.id
    ).all()
    
    for message in messages:
        messages_data.append({
            "id": message.id,
            "file_id": message.file_id,
            "key": message.key,
            "value": message.value,
            "created_by": message.created_by,
            "reviewed_by": message.reviewed_by
        })
    
    return {
        "id": file.id,
        "project_id": file.project_id,
        "created_by": file.created_by,
        "language_code": file.language_code,
        "language_name": file.language_name,
        "current_version": file.current_version,
        "created_at": file.created_at,
        "updated_at": file.updated_at,
        "messages": messages_data
    }


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
        logger.debug(f"Creating translation file for language {data.language_code} in project {project_id}")
        
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
        db.refresh(file)
        logger.info(f"Translation file created with id: {file.id}")
        return file

    @staticmethod
    def get_file(db: Session, file_id: UUID) -> TranslationFile:
        """Get a translation file by ID"""
        logger.debug(f"Fetching translation file {file_id}")
        
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)
        return file

    @staticmethod
    def list_files(db: Session, project_id: UUID) -> list:
        """List all translation files in a project"""
        logger.debug(f"Listing translation files for project {project_id}")
        
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
        logger.debug(f"Updating translation file {file_id}")
        
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
        file.updated_at = datetime.now(timezone.utc)
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
        db.refresh(file)
        logger.info(f"Translation file {file_id} updated")
        return file

    @staticmethod
    def delete_file(db: Session, file_id: UUID, user_id: UUID, project_id: UUID) -> None:
        """Delete a translation file - RBAC: ADMIN only"""
        logger.debug(f"Deleting translation file {file_id}")
        
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
        language_code = file.language_code
        db.delete(file)
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.TRANSLATION_FILE,
            entity_id=file_id_to_log,
            details={"language_code": language_code},
        )
        db.add(audit)
        db.commit()
        logger.info(f"Translation file {file_id} deleted")

    @staticmethod
    def export_file(db: Session, file_id: UUID) -> dict:
        """Export file as JSON with all messages"""
        logger.debug(f"Exporting translation file {file_id}")
        
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)

        messages = db.query(Message).filter_by(file_id=file_id).all()
        export_data = {
            "language_code": file.language_code,
            "language_name": file.language_name,
            "version": file.current_version,
            "messages": [
                {
                    "key": m.key,
                    "value": m.value,
                    "status": m.status.value,
                    "comment": m.comment,
                }
                for m in messages
            ],
            "exported_at": datetime.now(timezone.utc),
        }
        logger.info(f"Translation file {file_id} exported with {len(messages)} messages")
        return export_data

    @staticmethod
    def get_version_history(db: Session, file_id: UUID) -> list:
        """Get all versions of a translation file"""
        logger.debug(f"Fetching version history for file {file_id}")
        
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)
        return db.query(TranslationVersion).filter_by(file_id=file_id).all()

    @staticmethod
    def get_file_detailed(db: Session, file_id: UUID) -> dict:
        """Get translation file with messages details"""
        logger.debug(f"Fetching detailed translation file {file_id}")
        
        file = db.query(TranslationFile).filter_by(id=file_id).first()
        if not file:
            raise FileNotFoundException(file_id)
        
        return _build_translation_file_detailed(db, file)

    @staticmethod
    def list_files_detailed(db: Session, project_id: UUID) -> list:
        """List all translation files in project with messages details"""
        logger.debug(f"Listing detailed translation files for project {project_id}")
        
        files = db.query(TranslationFile).filter_by(project_id=project_id).all()
        return [_build_translation_file_detailed(db, file) for file in files]

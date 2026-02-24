from uuid import UUID
from sqlalchemy.orm import Session
from ..entities.project import Project
from ..entities.projectMember import ProjectMember
from ..entities.auditLog import AuditLog
from ..entities.enums import ProjectRole, AuditAction, AuditEntityType
from ..exceptions import (
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
    UnauthorizedException,
)
from .models import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for managing projects"""

    @staticmethod
    def create_project(
        db: Session,
        organization_id: UUID,
        user_id: UUID,
        data: ProjectCreate,
    ) -> Project:
        """Create a new project - creator becomes ADMIN"""
        # Check if project with same name already exists in org
        existing = db.query(Project).filter_by(
            organization_id=organization_id, name=data.name
        ).first()
        if existing:
            raise ProjectAlreadyExistsException(data.name)

        project = Project(
            organization_id=organization_id,
            created_by=user_id,
            name=data.name,
            description=data.description,
            source_language=data.source_language,
            target_languages=",".join(data.target_languages),
        )
        db.add(project)
        db.flush()

        # Add creator as ADMIN member
        member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role=ProjectRole.ADMIN,
        )
        db.add(member)
        db.flush()

        # Audit log for project creation
        audit = AuditLog(
            user_id=user_id,
            project_id=project.id,
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.PROJECT,
            entity_id=project.id,
            details={
                "name": data.name,
                "source_language": data.source_language,
                "target_languages": data.target_languages,
            },
        )
        db.add(audit)
        db.commit()
        return project

    @staticmethod
    def get_project(db: Session, project_id: UUID) -> Project:
        """Get a project by ID"""
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)
        return project

    @staticmethod
    def list_projects(db: Session, organization_id: UUID) -> list:
        """List all projects in an organization"""
        return db.query(Project).filter_by(organization_id=organization_id).all()

    @staticmethod
    def list_user_projects(db: Session, user_id: UUID) -> list:
        """List all projects a user is a member of"""
        members = db.query(ProjectMember).filter_by(user_id=user_id).all()
        project_ids = [m.project_id for m in members]
        if not project_ids:
            return []
        return db.query(Project).filter(Project.id.in_(project_ids)).all()

    @staticmethod
    def update_project(
        db: Session,
        project_id: UUID,
        user_id: UUID,
        data: ProjectUpdate,
    ) -> Project:
        """Update a project - RBAC: ADMIN only"""
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)

        # Check member permissions - ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can update projects")

        if data.name:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.target_languages:
            project.target_languages = ",".join(data.target_languages)

        project.updated_at = None
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id,
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.PROJECT,
            entity_id=project_id,
            details={
                "name": project.name,
                "target_languages": project.target_languages,
            },
        )
        db.add(audit)
        db.commit()
        return project

    @staticmethod
    def delete_project(db: Session, project_id: UUID, user_id: UUID) -> None:
        """Delete a project - RBAC: ADMIN only"""
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)

        # Check member permissions - ADMIN only
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if not member or member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can delete projects")

        project_id_to_log = project.id
        db.delete(project)
        db.flush()

        audit = AuditLog(
            user_id=user_id,
            project_id=project_id_to_log,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.PROJECT,
            entity_id=project_id_to_log,
            details={"name": project.name},
        )
        db.add(audit)
        db.commit()

    @staticmethod
    def get_project_stats(db: Session, project_id: UUID) -> dict:
        """Get statistics about a project"""
        project = db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)

        from ..entities.translationFile import TranslationFile
        from ..entities.message import Message

        file_count = db.query(TranslationFile).filter_by(project_id=project_id).count()
        total_messages = db.query(Message).join(TranslationFile).filter(
            TranslationFile.project_id == project_id
        ).count()
        member_count = db.query(ProjectMember).filter_by(project_id=project_id).count()

        return {
            "project_id": project_id,
            "name": project.name,
            "files": file_count,
            "total_messages": total_messages,
            "members": member_count,
        }

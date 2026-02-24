from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..entities.project import Project
from ..entities.projectMember import ProjectMember
from ..entities.enums import ProjectRole
from ..exceptions import (
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
    UnauthorizedException,
)
from .models import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project management with RBAC and validation"""

    @staticmethod
    def create_project(
        db: Session,
        user_id: UUID,
        org_id: UUID,
        project_data: ProjectCreate,
    ) -> Project:
        """Create a new project. User must be OWNER or ADMIN in organization."""
        # Check if project with same name already exists in this org
        existing = db.query(Project).filter(
            and_(
                Project.organization_id == org_id,
                Project.name == project_data.name,
            )
        ).first()
        if existing:
            raise ProjectAlreadyExistsException(project_data.name)

        # Create project
        project = Project(
            organization_id=org_id,
            created_by=user_id,
            name=project_data.name,
            description=project_data.description,
            source_language=project_data.source_language,
            target_languages=",".join(project_data.target_languages),
        )
        db.add(project)
        db.flush()

        # Add creator as LEAD member
        member = ProjectMember(
            project_id=project.id,
            user_id=user_id,
            role=ProjectRole.LEAD,
        )
        db.add(member)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project(db: Session, project_id: UUID) -> Project:
        """Get project by ID"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ProjectNotFoundException(project_id)
        return project

    @staticmethod
    def update_project(
        db: Session,
        user_id: UUID,
        project_id: UUID,
        project_data: ProjectUpdate,
    ) -> Project:
        """Update project. Only LEAD members can update."""
        project = ProjectService.get_project(db, project_id)

        # Check RBAC - user must be LEAD
        member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        ).first()
        if not member or member.role != ProjectRole.LEAD:
            raise UnauthorizedException("Only LEAD members can update project")

        # Update fields
        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description
        if project_data.target_languages is not None:
            project.target_languages = ",".join(project_data.target_languages)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def list_projects(db: Session, org_id: UUID) -> list[Project]:
        """List all projects in an organization"""
        return db.query(Project).filter(Project.organization_id == org_id).all()

    @staticmethod
    def delete_project(
        db: Session,
        user_id: UUID,
        project_id: UUID,
    ) -> None:
        """Delete project. Only LEAD members can delete."""
        project = ProjectService.get_project(db, project_id)

        # Check RBAC - user must be LEAD
        member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        ).first()
        if not member or member.role != ProjectRole.LEAD:
            raise UnauthorizedException("Only LEAD members can delete project")

        db.delete(project)
        db.commit()

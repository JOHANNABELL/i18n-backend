from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging
from ..entities.projectMember import ProjectMember
from ..entities.auditLog import AuditLog
from ..entities.enums import ProjectRole, AuditAction, AuditEntityType
from ..exceptions import (
    MemberAlreadyExistsException,
    CannotRemoveLastLeadException,
    UnauthorizedException,
    MemberNotFoundException,
)
from .models import ProjectMemberCreate, ProjectMemberUpdate


logger = logging.getLogger(__name__)


class ProjectMemberService:
    """Service for managing project members"""

    @staticmethod
    def add_member(
        db: Session,
        project_id: UUID,
        user_id: UUID,
        added_by: UUID,
        data: ProjectMemberCreate,
    ) -> ProjectMember:
        """Add a member to a project - RBAC: ADMIN only"""
        logger.debug(f"Adding member {data.user_id} to project {project_id}")
        
        # Check if member already exists
        existing = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=data.user_id
        ).first()
        if existing:
            raise MemberAlreadyExistsException(data.user_id)

        # Check adder permissions - ADMIN only
        adder_member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=added_by
        ).first()
        if not adder_member or adder_member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can add members")

        member = ProjectMember(
            project_id=project_id,
            user_id=data.user_id,
            role=data.role,
        )
        db.add(member)
        db.flush()

        audit = AuditLog(
            user_id=added_by,
            project_id=project_id,
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.PROJECT_MEMBER,
            entity_id=member.id,
            details={"user_id": str(data.user_id), "role": data.role.value},
        )
        db.add(audit)
        db.commit()
        db.refresh(member)
        logger.info(f"Member {data.user_id} added to project {project_id}")
        return member

    @staticmethod
    def get_member(db: Session, member_id: UUID) -> ProjectMember:
        """Get a project member by ID"""
        logger.debug(f"Fetching member {member_id}")
        member = db.query(ProjectMember).filter_by(id=member_id).first()
        if not member:
            raise MemberNotFoundException(member_id)
        return member

    @staticmethod
    def list_members(db: Session, project_id: UUID) -> list:
        """List all members in a project"""
        logger.debug(f"Listing members for project {project_id}")
        return db.query(ProjectMember).filter_by(project_id=project_id).all()

    @staticmethod
    def update_member_role(
        db: Session,
        member_id: UUID,
        project_id: UUID,
        updated_by: UUID,
        data: ProjectMemberUpdate,
    ) -> ProjectMember:
        """Update a member's role - RBAC: ADMIN only"""
        logger.debug(f"Updating member {member_id} role to {data.role}")
        
        member = db.query(ProjectMember).filter_by(id=member_id).first()
        if not member:
            raise MemberNotFoundException(member_id)

        # Check updater permissions - ADMIN only
        updater_member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=updated_by
        ).first()
        if not updater_member or updater_member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can update member roles")

        old_role = member.role
        member.role = data.role
        member.updated_at = datetime.now(timezone.utc)
        db.flush()

        audit = AuditLog(
            user_id=updated_by,
            project_id=project_id,
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.PROJECT_MEMBER,
            entity_id=member.id,
            details={
                "user_id": str(member.user_id),
                "old_role": old_role.value,
                "new_role": data.role.value,
            },
        )
        db.add(audit)
        db.commit()
        db.refresh(member)
        logger.info(f"Member {member_id} role updated to {data.role}")
        return member

    @staticmethod
    def remove_member(db: Session, member_id: UUID, project_id: UUID, removed_by: UUID) -> None:
        """Remove a member from a project - RBAC: ADMIN only"""
        logger.debug(f"Removing member {member_id} from project {project_id}")
        
        member = db.query(ProjectMember).filter_by(id=member_id).first()
        if not member:
            raise MemberNotFoundException(member_id)

        # Check remover permissions - ADMIN only
        remover_member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=removed_by
        ).first()
        if not remover_member or remover_member.role != ProjectRole.ADMIN:
            raise UnauthorizedException("Only ADMIN can remove members")

        # Check if removing last LEAD
        if member.role == ProjectRole.LEAD:
            lead_count = db.query(ProjectMember).filter_by(
                project_id=project_id, role=ProjectRole.LEAD
            ).count()
            if lead_count == 1:
                raise CannotRemoveLastLeadException()

        member_id_to_log = member.id
        user_id_to_log = member.user_id
        db.delete(member)
        db.flush()

        audit = AuditLog(
            user_id=removed_by,
            project_id=project_id,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.PROJECT_MEMBER,
            entity_id=member_id_to_log,
            details={"user_id": str(user_id_to_log)},
        )
        db.add(audit)
        db.commit()
        logger.info(f"Member {member_id} removed from project {project_id}")

    @staticmethod
    def get_user_role_in_project(db: Session, project_id: UUID, user_id: UUID) -> ProjectRole:
        """Get a user's role in a project"""
        logger.debug(f"Fetching user {user_id} role in project {project_id}")
        member = db.query(ProjectMember).filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        return member.role if member else None

"""
Test Role-Based Access Control (RBAC) enforcement across all services
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from src.entities.projectMember import ProjectMember
from src.entities.enums import ProjectRole
from src.exceptions import UnauthorizedException
from src.project.service import ProjectService
from src.projectMember.service import ProjectMemberService
from src.message.service import MessageService
from src.translationFile.service import TranslationFileService
from src.project.models import ProjectCreate
from src.message.models import MessageCreate


class TestProjectRBAC:
    """Test project-level RBAC"""

    def test_only_admin_can_update_project(self, db: Session):
        """Only ADMIN members can update project details"""
        from src.entities.project import Project
        from src.project.models import ProjectUpdate

        project_id = uuid4()
        org_id = uuid4()
        admin_id = uuid4()
        editor_id = uuid4()

        # Create project
        project = Project(
            id=project_id,
            organization_id=org_id,
            name="Test Project",
            source_language="en",
            target_languages="es,fr",
        )
        db.add(project)
        db.flush()

        # Add admin and editor members
        admin_member = ProjectMember(
            project_id=project_id, user_id=admin_id, role=ProjectRole.ADMIN
        )
        editor_member = ProjectMember(
            project_id=project_id, user_id=editor_id, role=ProjectRole.EDITOR
        )
        db.add(admin_member)
        db.add(editor_member)
        db.commit()

        # Admin can update
        update = ProjectUpdate(name="Updated Project")
        result = ProjectService.update_project(db, project_id, admin_id, update)
        assert result.name == "Updated Project"

        # Editor cannot update
        update2 = ProjectUpdate(name="Another Update")
        with pytest.raises(UnauthorizedException):
            ProjectService.update_project(db, project_id, editor_id, update2)


class TestMessageRBAC:
    """Test message-level RBAC"""

    def test_viewer_cannot_create_message(self, db: Session):
        """VIEWER members cannot create messages"""
        from src.entities.translationFile import TranslationFile

        file_id = uuid4()
        project_id = uuid4()
        viewer_id = uuid4()

        file = TranslationFile(
            id=file_id,
            project_id=project_id,
            language_code="es",
            language_name="Spanish",
        )
        db.add(file)
        db.flush()

        # Add viewer member
        viewer_member = ProjectMember(
            project_id=project_id, user_id=viewer_id, role=ProjectRole.VIEWER
        )
        db.add(viewer_member)
        db.commit()

        # Viewer cannot create message
        message_data = MessageCreate(key="greeting", value="Hola")
        with pytest.raises(UnauthorizedException):
            MessageService.create_message(db, file_id, viewer_id, message_data, project_id)

    def test_only_lead_admin_can_approve_message(self, db: Session):
        """Only LEAD and ADMIN can approve messages"""
        from src.entities.message import Message

        message_id = uuid4()
        project_id = uuid4()
        file_id = uuid4()
        lead_id = uuid4()
        editor_id = uuid4()

        message = Message(
            id=message_id,
            file_id=file_id,
            key="greeting",
            value="Hello",
            status=MessageStatus.PENDING,
        )
        db.add(message)
        db.flush()

        # Add lead and editor members
        lead_member = ProjectMember(
            project_id=project_id, user_id=lead_id, role=ProjectRole.LEAD
        )
        editor_member = ProjectMember(
            project_id=project_id, user_id=editor_id, role=ProjectRole.EDITOR
        )
        db.add(lead_member)
        db.add(editor_member)
        db.commit()

        # Lead can approve
        result = MessageService.approve_message(db, message_id, lead_id, project_id)
        assert result.status == MessageStatus.APPROVED

        # Create another pending message
        message2_id = uuid4()
        message2 = Message(
            id=message2_id,
            file_id=file_id,
            key="farewell",
            value="Goodbye",
            status=MessageStatus.PENDING,
        )
        db.add(message2)
        db.commit()

        # Editor cannot approve
        with pytest.raises(UnauthorizedException):
            MessageService.approve_message(db, message2_id, editor_id, project_id)

    def test_only_admin_can_delete_message(self, db: Session):
        """Only ADMIN can delete messages"""
        from src.entities.message import Message

        message_id = uuid4()
        project_id = uuid4()
        file_id = uuid4()
        admin_id = uuid4()
        editor_id = uuid4()

        message = Message(
            id=message_id,
            file_id=file_id,
            key="greeting",
            value="Hello",
        )
        db.add(message)
        db.flush()

        # Add admin and editor members
        admin_member = ProjectMember(
            project_id=project_id, user_id=admin_id, role=ProjectRole.ADMIN
        )
        editor_member = ProjectMember(
            project_id=project_id, user_id=editor_id, role=ProjectRole.EDITOR
        )
        db.add(admin_member)
        db.add(editor_member)
        db.commit()

        # Admin can delete
        MessageService.delete_message(db, message_id, admin_id, project_id)
        assert db.query(Message).filter_by(id=message_id).first() is None

        # Create another message for editor test
        message2_id = uuid4()
        message2 = Message(
            id=message2_id,
            file_id=file_id,
            key="farewell",
            value="Goodbye",
        )
        db.add(message2)
        db.commit()

        # Editor cannot delete
        with pytest.raises(UnauthorizedException):
            MessageService.delete_message(db, message2_id, editor_id, project_id)


class TestProjectMemberRBAC:
    """Test project member management RBAC"""

    def test_only_admin_can_add_member(self, db: Session):
        """Only ADMIN can add new members"""
        from src.projectMember.models import ProjectMemberCreate

        project_id = uuid4()
        admin_id = uuid4()
        editor_id = uuid4()
        new_user_id = uuid4()

        # Add admin and editor members
        admin_member = ProjectMember(
            project_id=project_id, user_id=admin_id, role=ProjectRole.ADMIN
        )
        editor_member = ProjectMember(
            project_id=project_id, user_id=editor_id, role=ProjectRole.EDITOR
        )
        db.add(admin_member)
        db.add(editor_member)
        db.commit()

        # Admin can add member
        add_data = ProjectMemberCreate(user_id=new_user_id, role=ProjectRole.EDITOR)
        result = ProjectMemberService.add_member(
            db, project_id, admin_id, new_user_id, add_data
        )
        assert result.user_id == new_user_id

        # Editor cannot add member
        another_user_id = uuid4()
        add_data2 = ProjectMemberCreate(user_id=another_user_id, role=ProjectRole.VIEWER)
        with pytest.raises(UnauthorizedException):
            ProjectMemberService.add_member(
                db, project_id, editor_id, another_user_id, add_data2
            )

    def test_cannot_remove_last_lead(self, db: Session):
        """Cannot remove the last LEAD member"""
        from src.exceptions import CannotRemoveLastLeadException

        project_id = uuid4()
        lead_id = uuid4()
        admin_id = uuid4()

        # Create LEAD and ADMIN
        lead_member = ProjectMember(
            id=uuid4(), project_id=project_id, user_id=lead_id, role=ProjectRole.LEAD
        )
        admin_member = ProjectMember(
            id=uuid4(),
            project_id=project_id,
            user_id=admin_id,
            role=ProjectRole.ADMIN,
        )
        db.add(lead_member)
        db.add(admin_member)
        db.commit()

        # Try to remove last LEAD
        with pytest.raises(CannotRemoveLastLeadException):
            ProjectMemberService.remove_member(db, lead_member.id, project_id, admin_id)

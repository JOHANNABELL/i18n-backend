from fastapi import HTTPException

class TodoError(HTTPException):
    """Base exception for todo-related errors"""
    pass

class TodoNotFoundError(TodoError):
    def __init__(self, todo_id=None):
        message = "Todo not found" if todo_id is None else f"Todo with id {todo_id} not found"
        super().__init__(status_code=404, detail=message)

class TodoCreationError(TodoError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create todo: {error}")

class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass

class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)

class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New passwords do not match")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)


# Organization-related exceptions
class OrgError(HTTPException):
    """Base exception for organization-related errors"""
    pass

class OrgNotFoundException(OrgError):
    def __init__(self, org_id=None):
        message = "Organization not found" if org_id is None else f"Organization with id {org_id} not found"
        super().__init__(status_code=404, detail=message)

class UserNotInOrgException(OrgError):
    def __init__(self, user_id=None):
        message = "User is not a member of this organization"
        super().__init__(status_code=403, detail=message)


# Project-related exceptions
class ProjectError(HTTPException):
    """Base exception for project-related errors"""
    pass

class ProjectAlreadyExistsException(ProjectError):
    def __init__(self, project_name):
        super().__init__(status_code=409, detail=f"Project '{project_name}' already exists in this organization")

class ProjectNotFoundException(ProjectError):
    def __init__(self, project_id=None):
        message = "Project not found" if project_id is None else f"Project with id {project_id} not found"
        super().__init__(status_code=404, detail=message)


# Project Member-related exceptions
class MemberError(HTTPException):
    """Base exception for project member-related errors"""
    pass

class MemberAlreadyExistsException(MemberError):
    def __init__(self, user_id=None):
        message = "User is already a member of this project"
        super().__init__(status_code=409, detail=message)

class CannotRemoveLastLeadException(MemberError):
    def __init__(self):
        super().__init__(status_code=409, detail="Cannot remove the last LEAD member from the project")


# Translation File-related exceptions
class FileError(HTTPException):
    """Base exception for translation file-related errors"""
    pass

class FileAlreadyExistsException(FileError):
    def __init__(self, language_code):
        super().__init__(status_code=409, detail=f"Translation file for language '{language_code}' already exists")

class FileNotFoundException(FileError):
    def __init__(self, file_id=None):
        message = "Translation file not found" if file_id is None else f"Translation file with id {file_id} not found"
        super().__init__(status_code=404, detail=message)

class LanguageNotAllowedException(FileError):
    def __init__(self, language_code):
        super().__init__(status_code=422, detail=f"Language '{language_code}' is not in the target languages for this project")


# Message-related exceptions
class MessageError(HTTPException):
    """Base exception for message-related errors"""
    pass

class KeyAlreadyExistsException(MessageError):
    def __init__(self, key):
        super().__init__(status_code=409, detail=f"Message key '{key}' already exists in this file")

class MessageNotFoundException(MessageError):
    def __init__(self, message_id=None):
        message = "Message not found" if message_id is None else f"Message with id {message_id} not found"
        super().__init__(status_code=404, detail=message)

class InvalidStatusTransitionException(MessageError):
    def __init__(self, current_status, target_status):
        super().__init__(status_code=422, detail=f"Cannot transition from {current_status} to {target_status}")


# Authorization exceptions
class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(status_code=403, detail=message)

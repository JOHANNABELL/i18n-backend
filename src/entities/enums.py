import enum

class OrgRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class ProjectRole(str, enum.Enum):
    LEAD = "LEAD"
    TRANSLATOR = "TRANSLATOR"
    REVIEWER = "REVIEWER"

class TranslationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class NotificationType(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"

class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
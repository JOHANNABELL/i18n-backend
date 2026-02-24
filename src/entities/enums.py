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

class MessageStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AuditEntityType(str, enum.Enum):
    PROJECT = "PROJECT"
    TRANSLATION_FILE = "TRANSLATION_FILE"
    MESSAGE = "MESSAGE"
    TRANSLATION_VERSION = "TRANSLATION_VERSION"
    PROJECT_MEMBER = "PROJECT_MEMBER"
class Priority (str, enum.Enum):
    TOP = "TOP"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH" 
    NORMAL = "NORMAL"   
    

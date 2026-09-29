import enum


class Role(str, enum.Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    HOD = "HOD"
    ADMIN = "ADMIN"


class RecordStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class SessionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"


class GatePassStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Priority(str, enum.Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    URGENT = "URGENT"


class AudienceType(str, enum.Enum):
    ALL_STUDENTS = "ALL_STUDENTS"
    DEPARTMENT = "DEPARTMENT"
    SEMESTER = "SEMESTER"
    SECTION = "SECTION"
    SPECIFIC_GROUP = "SPECIFIC_GROUP"


class NotificationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

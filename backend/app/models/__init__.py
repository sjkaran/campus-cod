"""Import every model so Base.metadata (Alembic, tests) sees all tables."""
from app.models.academic_class import AcademicClass
from app.models.admin import Admin
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.audit_log import AuditLog
from app.models.department import Department
from app.models.enums import (
    AttendanceStatus, AudienceType, GatePassStatus, NotificationStatus, Priority,
    RecordStatus, Role, SessionStatus,
)
from app.models.faculty import Faculty, FacultyAssignment
from app.models.gatepass import GatePass
from app.models.hod import Hod
from app.models.notification import Notification, NotificationRead, NotificationTarget
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User

__all__ = [
    "AcademicClass", "Admin", "AttendanceRecord", "AttendanceSession", "AuditLog", "Department",
    "Faculty", "FacultyAssignment", "GatePass", "Hod", "Notification", "NotificationRead",
    "NotificationTarget", "Student", "Subject", "User",
    "AttendanceStatus", "AudienceType", "GatePassStatus", "NotificationStatus", "Priority",
    "RecordStatus", "Role", "SessionStatus",
]

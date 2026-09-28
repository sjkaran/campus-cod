"""Client-side domain models (not the final DB schema)."""
from dataclasses import dataclass, field
from typing import List, Optional

DRAFT, ACTIVE, CLOSED, READY, SUBMITTED, FAILED = (
    "DRAFT", "ACTIVE", "CLOSED", "READY_FOR_SUBMISSION", "SUBMITTED", "SUBMISSION_FAILED")

@dataclass
class Faculty:
    faculty_id: str; name: str; department: str

@dataclass
class Student:
    student_id: str; name: str; roll_no: str

@dataclass
class Subject:
    subject_id: str; name: str; code: str; department_id: str

@dataclass
class AcademicGroup:
    department_id: str; department: str; semester: int; section: str

@dataclass
class AttendanceSession:
    session_id: str; faculty_id: str; department_id: str; semester: int; section: str
    subject_id: str; subject_name: str; date: str; start_time: str; end_time: str = ""
    status: str = ACTIVE; submission_id: Optional[str] = None

@dataclass
class AttendanceRecord:
    student_id: str; session_id: str; status: str; marked_at: str = ""

@dataclass
class AttendanceReport:
    session: AttendanceSession
    total_students: int = 0; present: int = 0; absent: int = 0
    attendance_percentage: float = 0.0
    records: List[AttendanceRecord] = field(default_factory=list)
    rejected_scans: int = 0

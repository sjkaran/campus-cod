from app.models.enums import RecordStatus
from app.schemas.common import ORMModel
from pydantic import BaseModel


class StudentResponse(ORMModel):
    id: int
    student_id: str
    roll_number: str
    name: str
    email: str
    phone: str | None
    department_id: int
    department_code: str
    semester: int
    section: str
    status: RecordStatus


class AttendanceSummary(BaseModel):
    total_classes: int
    present: int
    absent: int
    percentage: float


class SubjectAttendance(AttendanceSummary):
    subject_id: int
    subject_code: str
    subject_name: str


class StudentAttendanceResponse(BaseModel):
    overall: AttendanceSummary
    subjects: list[SubjectAttendance]

from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import GatePassStatus


class AttendanceReportRow(BaseModel):
    student_id: str
    student_name: str
    department_code: str
    semester: int
    section: str
    subject_code: str
    subject_name: str
    total_classes: int
    present: int
    absent: int
    percentage: float


class StudentReportRow(BaseModel):
    student_id: str
    roll_number: str
    name: str
    email: str
    department_code: str
    semester: int
    section: str
    status: str


class GatePassReportRow(BaseModel):
    id: int
    student_id: str
    student_name: str
    department_code: str
    destination: str
    departure_date: date
    return_date: date
    status: GatePassStatus
    hod_name: str | None
    created_at: datetime
    reviewed_at: datetime | None

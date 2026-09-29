from pydantic import BaseModel

from app.schemas.student import AttendanceSummary


class GatePassCounts(BaseModel):
    pending: int
    approved: int
    rejected: int
    cancelled: int
    total: int


class OverviewResponse(BaseModel):
    scope: str  # "INSTITUTION" | "DEPARTMENT" | "FACULTY"
    students: int | None = None
    faculty: int | None = None
    departments: int | None = None
    attendance: AttendanceSummary
    low_attendance_students: int | None = None
    gate_passes: GatePassCounts | None = None


class LowAttendanceStudent(BaseModel):
    student_id: str
    name: str
    department_code: str
    semester: int
    section: str
    summary: AttendanceSummary


class AttendanceAnalyticsResponse(BaseModel):
    overall: AttendanceSummary
    threshold: float
    low_attendance: list[LowAttendanceStudent]


class GroupAttendance(BaseModel):
    key: str
    label: str
    summary: AttendanceSummary

from datetime import date, datetime, time

from pydantic import BaseModel, Field, model_validator

from app.models.enums import AttendanceStatus, SessionStatus
from app.schemas.common import ORMModel


class AttendanceSessionCreate(BaseModel):
    external_session_id: str | None = Field(default=None, max_length=64)
    subject_id: int
    academic_class_id: int
    date: date
    start_time: time | None = None
    end_time: time | None = None

    @model_validator(mode="after")
    def _times(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class SessionStatusUpdate(BaseModel):
    """Faculty-driven transitions. SUBMITTED is only reachable via the submit endpoint."""
    status: SessionStatus


class AttendanceRecordInput(BaseModel):
    student_id: str = Field(min_length=1, max_length=32, description="Public student ID, e.g. S2026001")
    status: AttendanceStatus
    marked_at: datetime | None = None


class AttendanceSubmit(BaseModel):
    records: list[AttendanceRecordInput] = Field(min_length=1, max_length=1000)


class AttendanceRecordResponse(ORMModel):
    id: int
    student_id: int
    student_public_id: str | None = None
    student_name: str | None = None
    status: AttendanceStatus
    marked_at: datetime | None


class AttendanceSessionResponse(ORMModel):
    id: int
    external_session_id: str | None
    faculty_id: int
    faculty_name: str
    subject_id: int
    subject_code: str
    subject_name: str
    academic_class_id: int
    class_label: str
    date: date
    start_time: time | None
    end_time: time | None
    status: SessionStatus
    created_at: datetime
    finalized_at: datetime | None
    submitted_at: datetime | None


class AttendanceSessionDetail(AttendanceSessionResponse):
    records: list[AttendanceRecordResponse] = []


class AttendanceSessionSummary(AttendanceSessionResponse):
    present: int = 0
    absent: int = 0
    percentage: float = 0.0


class SubmissionResult(BaseModel):
    success: bool
    session_id: int
    status: SessionStatus
    total: int
    present: int
    absent: int

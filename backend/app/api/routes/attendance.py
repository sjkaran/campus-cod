from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.responses import COMMON_ERRORS, ok, paged
from app.core.dependencies import current_faculty, require_roles
from app.database.database import get_db
from app.models import Faculty, Role, SessionStatus, User
from app.schemas.attendance import (
    AttendanceSessionCreate, AttendanceSessionDetail, AttendanceSessionResponse,
    AttendanceSessionSummary, AttendanceSubmit, SessionStatusUpdate, SubmissionResult,
)
from app.schemas.common import DataResponse, ErrorResponse, PagedResponse
from app.services import attendance_service
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/attendance", tags=["Attendance"], responses=COMMON_ERRORS)

_conflict = {409: {"model": ErrorResponse, "description": "Invalid state transition or duplicate"}}


@router.post(
    "/sessions", status_code=201, response_model=DataResponse[AttendanceSessionResponse],
    summary="Create an attendance session (FACULTY, for an assigned subject/class)", responses=_conflict,
)
def create_session(body: AttendanceSessionCreate, faculty: Faculty = Depends(current_faculty), db: Session = Depends(get_db)):
    return ok(AttendanceSessionResponse, attendance_service.create_session(db, faculty, body))


@router.get("/sessions/my", response_model=PagedResponse[AttendanceSessionSummary], summary="Own sessions (FACULTY)")
def my_sessions(
    status: SessionStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    params: PageParams = Depends(page_params),
    faculty: Faculty = Depends(current_faculty),
    db: Session = Depends(get_db),
):
    rows, total = attendance_service.my_sessions(db, faculty, status=status, date_from=date_from, date_to=date_to, params=params)
    return paged(None, [attendance_service.to_summary(s, p, t) for s, p, t in rows], total, params)


@router.get(
    "/sessions/{session_id}", response_model=DataResponse[AttendanceSessionDetail],
    summary="Session with per-student records (owner FACULTY, HOD of the department, ADMIN)",
)
def get_session(
    session_id: int,
    user: User = Depends(require_roles(Role.FACULTY, Role.HOD, Role.ADMIN)),
    db: Session = Depends(get_db),
):
    return {"data": attendance_service.get_detail(db, user, session_id)}


@router.patch(
    "/sessions/{session_id}/status", response_model=DataResponse[AttendanceSessionResponse],
    summary="Move own session along DRAFT -> ACTIVE -> CLOSED (or CANCELLED)", responses=_conflict,
)
def update_status(session_id: int, body: SessionStatusUpdate, faculty: Faculty = Depends(current_faculty), db: Session = Depends(get_db)):
    return ok(AttendanceSessionResponse, attendance_service.update_status(db, faculty, session_id, body))


@router.post(
    "/sessions/{session_id}/submit", response_model=SubmissionResult, responses=_conflict,
    summary="Submit finalised attendance for a CLOSED session (owner FACULTY)",
    description="Students on the class roster who are not listed are recorded ABSENT. "
                "Records for students outside the class are rejected (400); duplicates are rejected (409).",
)
def submit(session_id: int, body: AttendanceSubmit, faculty: Faculty = Depends(current_faculty), db: Session = Depends(get_db)):
    return attendance_service.submit(db, faculty, session_id, body)


def _summaries(db, user, department, semester, section, subject, on_date, date_from, date_to, status, params):
    if on_date:
        date_from = date_to = on_date
    items, total = attendance_service.list_summaries(
        db, user, department=department, semester=semester, section=section, subject=subject,
        date_from=date_from, date_to=date_to, status=status, params=params,
    )
    return paged(None, items, total, params)


@router.get("/department", response_model=PagedResponse[AttendanceSessionSummary], summary="Department attendance sessions (HOD)")
def department_attendance(
    semester: int | None = Query(None, ge=1, le=12), section: str | None = Query(None, max_length=8),
    subject: str | None = Query(None, max_length=24, description="Subject code"),
    on_date: date | None = Query(None, alias="date"), date_from: date | None = None, date_to: date | None = None,
    status: SessionStatus | None = None,
    params: PageParams = Depends(page_params),
    user: User = Depends(require_roles(Role.HOD)), db: Session = Depends(get_db),
):
    return _summaries(db, user, None, semester, section, subject, on_date, date_from, date_to, status, params)


@router.get("", response_model=PagedResponse[AttendanceSessionSummary], summary="Institution-wide attendance sessions (ADMIN)")
def all_attendance(
    department: str | None = Query(None, max_length=16, description="Department code"),
    semester: int | None = Query(None, ge=1, le=12), section: str | None = Query(None, max_length=8),
    subject: str | None = Query(None, max_length=24, description="Subject code"),
    on_date: date | None = Query(None, alias="date"), date_from: date | None = None, date_to: date | None = None,
    status: SessionStatus | None = None,
    params: PageParams = Depends(page_params),
    user: User = Depends(require_roles(Role.ADMIN)), db: Session = Depends(get_db),
):
    return _summaries(db, user, department, semester, section, subject, on_date, date_from, date_to, status, params)

import logging
from datetime import date, datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models import (
    AttendanceRecord, AttendanceSession, AttendanceStatus, Faculty, Role, SessionStatus, User,
)
from app.repositories.attendance_repository import AttendanceFilters, attendance_repo
from app.repositories.catalog_repository import catalog_repo
from app.repositories.student_repository import student_repo
from app.schemas.attendance import (
    AttendanceRecordResponse, AttendanceSessionCreate, AttendanceSessionDetail,
    AttendanceSessionResponse, AttendanceSessionSummary, AttendanceSubmit, SessionStatusUpdate,
    SubmissionResult,
)
from app.services import audit_service
from app.services.access import narrow_department, resolve_scope, resolve_subject_id
from app.utils.calculations import percentage
from app.utils.pagination import PageParams

log = logging.getLogger("app.attendance")

# Explicit state machine. Anything not listed is rejected with 409.
ALLOWED_TRANSITIONS: dict[SessionStatus, set[SessionStatus]] = {
    SessionStatus.DRAFT: {SessionStatus.ACTIVE, SessionStatus.CANCELLED},
    SessionStatus.ACTIVE: {SessionStatus.CLOSED, SessionStatus.CANCELLED},
    SessionStatus.CLOSED: {SessionStatus.SUBMITTED, SessionStatus.CANCELLED},
}
# SUBMITTED is only reachable through submit(), which validates the records.
FACULTY_SETTABLE = {SessionStatus.ACTIVE, SessionStatus.CLOSED, SessionStatus.CANCELLED}


def _own_session(db: Session, faculty: Faculty, session_id: int, *, for_update: bool = False) -> AttendanceSession:
    s = attendance_repo.get_session(db, session_id, for_update=for_update)
    if s is None or s.faculty_id != faculty.id:
        raise NotFoundError("Attendance session not found")
    return s


def create_session(db: Session, faculty: Faculty, data: AttendanceSessionCreate) -> AttendanceSession:
    if catalog_repo.get_subject(db, data.subject_id) is None or catalog_repo.get_class(db, data.academic_class_id) is None:
        raise NotFoundError("Subject or class not found")
    if not attendance_repo.has_assignment(db, faculty.id, data.subject_id, data.academic_class_id):
        raise ForbiddenError("You are not assigned to teach this subject to this class")
    if data.external_session_id and attendance_repo.external_id_exists(db, data.external_session_id):
        raise ConflictError("A session with this external_session_id already exists")

    s = AttendanceSession(
        external_session_id=data.external_session_id, faculty_id=faculty.id, subject_id=data.subject_id,
        academic_class_id=data.academic_class_id, date=data.date, start_time=data.start_time,
        end_time=data.end_time, status=SessionStatus.DRAFT,
    )
    try:
        attendance_repo.add_session(db, s)
        audit_service.record(db, user_id=faculty.user_id, action="ATTENDANCE_SESSION_CREATED",
                             resource_type="attendance_session", resource_id=s.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("A session with this external_session_id already exists")
    return attendance_repo.get_session(db, s.id)


def update_status(db: Session, faculty: Faculty, session_id: int, data: SessionStatusUpdate) -> AttendanceSession:
    s = _own_session(db, faculty, session_id, for_update=True)
    target = data.status
    if target == SessionStatus.SUBMITTED:
        raise BadRequestError("Use the submit endpoint to submit attendance")
    if target not in FACULTY_SETTABLE or target not in ALLOWED_TRANSITIONS.get(s.status, set()):
        raise ConflictError(f"Cannot change session status from {s.status.value} to {target.value}")
    s.status = target
    if target == SessionStatus.CLOSED:
        s.finalized_at = datetime.now(timezone.utc)
    audit_service.record(db, user_id=faculty.user_id, action=f"ATTENDANCE_SESSION_{target.value}",
                         resource_type="attendance_session", resource_id=s.id)
    db.commit()
    return attendance_repo.get_session(db, s.id)


def submit(db: Session, faculty: Faculty, session_id: int, data: AttendanceSubmit) -> SubmissionResult:
    """Validate -> derive full class roster -> persist records + finalise, all in ONE transaction."""
    s = _own_session(db, faculty, session_id, for_update=True)
    if s.status != SessionStatus.CLOSED:
        raise ConflictError(f"Session must be CLOSED to submit (current status: {s.status.value})")

    roster = student_repo.for_class(db, s.academic_class)
    if not roster:
        raise BadRequestError("This class has no active students")
    by_public_id = {st.student_id: st for st in roster}

    marks: dict[int, tuple[AttendanceStatus, datetime | None]] = {}
    for r in data.records:
        st = by_public_id.get(r.student_id)
        if st is None:
            raise BadRequestError(f"Student {r.student_id} does not belong to this class")
        if st.id in marks:
            raise ConflictError(f"Duplicate attendance record for student {r.student_id}")
        marks[st.id] = (r.status, r.marked_at)

    # Roster members the QR system did not report are ABSENT. The backend decides, not the client.
    records = [
        AttendanceRecord(
            session_id=s.id, student_id=st.id,
            status=marks[st.id][0] if st.id in marks else AttendanceStatus.ABSENT,
            marked_at=marks[st.id][1] if st.id in marks else None,
        )
        for st in roster
    ]
    present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    try:
        attendance_repo.add_records(db, records)
        s.status = SessionStatus.SUBMITTED
        s.submitted_at = datetime.now(timezone.utc)
        if s.finalized_at is None:
            s.finalized_at = s.submitted_at
        audit_service.record(
            db, user_id=faculty.user_id, action="ATTENDANCE_SUBMITTED", resource_type="attendance_session",
            resource_id=s.id, meta={"total": len(records), "present": present},
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Attendance for this session has already been recorded")
    log.info("attendance_submitted session_id=%s total=%s present=%s", s.id, len(records), present)
    return SubmissionResult(
        success=True, session_id=s.id, status=SessionStatus.SUBMITTED,
        total=len(records), present=present, absent=len(records) - present,
    )


def my_sessions(
    db: Session, faculty: Faculty, *, status: SessionStatus | None, date_from: date | None,
    date_to: date | None, params: PageParams,
):
    f = AttendanceFilters(faculty_id=faculty.id, date_from=date_from, date_to=date_to)
    return attendance_repo.list_sessions(db, f, params, statuses=[status] if status else None)


def get_detail(db: Session, user: User, session_id: int) -> AttendanceSessionDetail:
    s = attendance_repo.get_session(db, session_id)
    scope = resolve_scope(db, user)
    visible = s is not None and (
        scope.role == Role.ADMIN
        or (scope.role == Role.FACULTY and s.faculty_id == scope.faculty_id)
        or (scope.role == Role.HOD and s.academic_class.department_id == scope.department_id)
    )
    if not visible:
        raise NotFoundError("Attendance session not found")
    base = AttendanceSessionResponse.model_validate(s).model_dump()
    records = [AttendanceRecordResponse.model_validate(r) for r in attendance_repo.session_records(db, s.id)]
    return AttendanceSessionDetail(**base, records=records)


def list_summaries(
    db: Session, user: User, *, department: str | None, semester: int | None, section: str | None,
    subject: str | None, date_from: date | None, date_to: date | None, status: SessionStatus | None,
    params: PageParams,
):
    """ADMIN (institution) / HOD (own department) view of session-level attendance."""
    scope = resolve_scope(db, user)
    f = AttendanceFilters(
        department_id=narrow_department(db, scope, department), semester=semester, section=section,
        subject_id=resolve_subject_id(db, subject), date_from=date_from, date_to=date_to,
    )
    rows, total = attendance_repo.list_sessions(db, f, params, statuses=[status or SessionStatus.SUBMITTED])
    return [to_summary(s, present, count) for s, present, count in rows], total


def to_summary(s: AttendanceSession, present: int, total: int) -> AttendanceSessionSummary:
    base = AttendanceSessionResponse.model_validate(s).model_dump()
    return AttendanceSessionSummary(**base, present=present, absent=total - present, percentage=percentage(present, total))

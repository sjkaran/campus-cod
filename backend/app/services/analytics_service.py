from datetime import date

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.models import Department, Role, Subject, User
from app.repositories.attendance_repository import AttendanceFilters, attendance_repo
from app.repositories.catalog_repository import catalog_repo
from app.repositories.gatepass_repository import gatepass_repo
from app.repositories.student_repository import student_repo
from app.repositories.user_repository import user_repo
from app.schemas.analytics import (
    AttendanceAnalyticsResponse, GatePassCounts, GroupAttendance, LowAttendanceStudent, OverviewResponse,
)
from app.services.access import Scope, narrow_department, resolve_scope, resolve_subject_id
from app.utils.calculations import summarize


def _scope_and_filters(db: Session, user: User, department: str | None, **extra) -> tuple[Scope, AttendanceFilters, int | None]:
    """Department/faculty limits come from the token's owner, never from query params."""
    scope = resolve_scope(db, user)
    dept_id = narrow_department(db, scope, department)
    f = AttendanceFilters(department_id=dept_id, faculty_id=scope.faculty_id, **extra)
    return scope, f, dept_id


def overview(db: Session, user: User, department: str | None) -> OverviewResponse:
    scope, f, dept_id = _scope_and_filters(db, user, department)
    attendance = summarize(*attendance_repo.totals(db, f))
    if scope.role == Role.FACULTY:
        return OverviewResponse(scope="FACULTY", attendance=attendance)
    counts = gatepass_repo.count_by_status(db, dept_id)
    by = {s.value: n for s, n in counts.items()}
    return OverviewResponse(
        scope="INSTITUTION" if dept_id is None else "DEPARTMENT",
        students=student_repo.count(db, dept_id),
        faculty=user_repo.count_faculty(db, dept_id),
        departments=len(catalog_repo.departments(db)) if dept_id is None else 1,
        attendance=attendance,
        low_attendance_students=attendance_repo.low_attendance_count(db, f, settings.low_attendance_threshold),
        gate_passes=GatePassCounts(
            pending=by.get("PENDING", 0), approved=by.get("APPROVED", 0), rejected=by.get("REJECTED", 0),
            cancelled=by.get("CANCELLED", 0), total=sum(by.values()),
        ),
    )


def attendance(
    db: Session, user: User, *, department: str | None, semester: int | None, section: str | None,
    subject: str | None, date_from: date | None, date_to: date | None, threshold: float | None,
) -> AttendanceAnalyticsResponse:
    _, f, _ = _scope_and_filters(
        db, user, department, semester=semester, section=section,
        subject_id=resolve_subject_id(db, subject), date_from=date_from, date_to=date_to,
    )
    thr = threshold if threshold is not None else settings.low_attendance_threshold
    low = [
        LowAttendanceStudent(
            student_id=pid, name=name, department_code=dept, semester=sem, section=sec, summary=summarize(total, present)
        )
        for _, pid, name, dept, sem, sec, total, present in attendance_repo.low_attendance(db, f, thr)
    ]
    return AttendanceAnalyticsResponse(overall=summarize(*attendance_repo.totals(db, f)), threshold=thr, low_attendance=low)


def by_department(db: Session, user: User, department: str | None) -> list[GroupAttendance]:
    _, f, _ = _scope_and_filters(db, user, department)
    rows = attendance_repo.grouped(db, f, Department.code, Department.name)
    return [GroupAttendance(key=code, label=name, summary=summarize(t, p)) for code, name, t, p in rows]


def by_subject(db: Session, user: User, department: str | None) -> list[GroupAttendance]:
    _, f, _ = _scope_and_filters(db, user, department)
    rows = attendance_repo.grouped(db, f, Subject.code, Subject.name)
    return [GroupAttendance(key=code, label=name, summary=summarize(t, p)) for code, name, t, p in rows]


def gatepasses(db: Session, user: User, department: str | None) -> GatePassCounts:
    scope = resolve_scope(db, user)
    if scope.role == Role.FACULTY:
        raise ForbiddenError()
    dept_id = narrow_department(db, scope, department)
    by = {s.value: n for s, n in gatepass_repo.count_by_status(db, dept_id).items()}
    return GatePassCounts(
        pending=by.get("PENDING", 0), approved=by.get("APPROVED", 0), rejected=by.get("REJECTED", 0),
        cancelled=by.get("CANCELLED", 0), total=sum(by.values()),
    )

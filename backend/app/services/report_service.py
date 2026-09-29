"""One place that builds report rows, so JSON and CSV outputs can never disagree."""
import csv
import io
from datetime import date

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError
from app.models import GatePassStatus, Role, User
from app.repositories.attendance_repository import AttendanceFilters, attendance_repo
from app.repositories.student_repository import StudentFilters, student_repo
from app.schemas.reports import AttendanceReportRow, GatePassReportRow, StudentReportRow
from app.services import gatepass_service
from app.services.access import narrow_department, resolve_scope, resolve_subject_id
from app.utils.calculations import percentage
from app.utils.pagination import PageParams, paginate

MAX_EXPORT_ROWS = 10_000


def attendance_report(
    db: Session, user: User, *, department: str | None, semester: int | None, section: str | None,
    subject: str | None, date_from: date | None, date_to: date | None, params: PageParams,
):
    scope = resolve_scope(db, user)
    f = AttendanceFilters(
        department_id=narrow_department(db, scope, department), faculty_id=scope.faculty_id, semester=semester,
        section=section, subject_id=resolve_subject_id(db, subject), date_from=date_from, date_to=date_to,
    )
    rows, total = paginate(db, attendance_repo.student_subject_rows(db, f), params, scalars=False)
    items = [
        AttendanceReportRow(
            student_id=pid, student_name=name, department_code=dept, semester=sem, section=sec,
            subject_code=scode, subject_name=sname, total_classes=t, present=p, absent=t - p,
            percentage=percentage(p, t),
        )
        for pid, name, dept, sem, sec, scode, sname, t, p in rows
    ]
    return items, total


def students_report(
    db: Session, user: User, *, department: str | None, semester: int | None, section: str | None, params: PageParams,
):
    scope = resolve_scope(db, user)
    if scope.role == Role.FACULTY:
        raise ForbiddenError()
    dept_id = narrow_department(db, scope, department)
    students, total = student_repo.list(db, StudentFilters(dept_id, semester, section), params)
    items = [
        StudentReportRow(
            student_id=s.student_id, roll_number=s.roll_number, name=s.name, email=s.email,
            department_code=s.department_code, semester=s.semester, section=s.section, status=s.status.value,
        )
        for s in students
    ]
    return items, total


def gatepass_report(
    db: Session, user: User, *, department: str | None, status: GatePassStatus | None,
    date_from: date | None, date_to: date | None, params: PageParams,
):
    scope = resolve_scope(db, user)
    if scope.role == Role.FACULTY:
        raise ForbiddenError()
    dept_id = narrow_department(db, scope, department)
    gps, total = gatepass_service.list_for_staff(db, user, status, dept_id, params, date_from, date_to)
    items = [
        GatePassReportRow(
            id=g.id, student_id=g.student_public_id, student_name=g.student_name, department_code=g.department_code,
            destination=g.destination, departure_date=g.departure_date, return_date=g.return_date,
            status=g.status, hod_name=g.hod_name, created_at=g.created_at, reviewed_at=g.reviewed_at,
        )
        for g in gps
    ]
    return items, total


def to_csv(rows: list[BaseModel], columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for r in rows:
        data = r.model_dump(mode="json")
        # Neutralise spreadsheet formula injection in text cells.
        writer.writerow([("'" + v) if isinstance(v, str) and v and v[0] in "=+-@" else v for v in (data[c] for c in columns)])
    return buf.getvalue()

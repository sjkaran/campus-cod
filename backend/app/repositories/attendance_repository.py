from dataclasses import dataclass
from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AcademicClass, AttendanceRecord, AttendanceSession, AttendanceStatus, Department,
    FacultyAssignment, SessionStatus, Student, Subject,
)
from app.utils.pagination import PageParams, paginate


@dataclass
class AttendanceFilters:
    """Already-authorized filters. Scope (department/faculty/student) is injected by the service."""
    department_id: int | None = None
    semester: int | None = None
    section: str | None = None
    subject_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    faculty_id: int | None = None
    student_id: int | None = None


def _apply_session_filters(stmt, f: AttendanceFilters):
    """Requires AttendanceSession and AcademicClass to be part of the statement."""
    if f.faculty_id is not None:
        stmt = stmt.where(AttendanceSession.faculty_id == f.faculty_id)
    if f.department_id is not None:
        stmt = stmt.where(AcademicClass.department_id == f.department_id)
    if f.semester is not None:
        stmt = stmt.where(AcademicClass.semester == f.semester)
    if f.section:
        stmt = stmt.where(AcademicClass.section == f.section.upper())
    if f.subject_id is not None:
        stmt = stmt.where(AttendanceSession.subject_id == f.subject_id)
    if f.date_from:
        stmt = stmt.where(AttendanceSession.date >= f.date_from)
    if f.date_to:
        stmt = stmt.where(AttendanceSession.date <= f.date_to)
    return stmt


_PRESENT = func.coalesce(func.sum(case((AttendanceRecord.status == AttendanceStatus.PRESENT, 1), else_=0)), 0)
_TOTAL = func.count(AttendanceRecord.id)

_SESSION_LOAD = (
    joinedload(AttendanceSession.faculty),
    joinedload(AttendanceSession.subject),
    joinedload(AttendanceSession.academic_class).joinedload(AcademicClass.department),
)


class AttendanceRepository:
    # ---- sessions ---------------------------------------------------------
    def has_assignment(self, db: Session, faculty_id: int, subject_id: int, class_id: int) -> bool:
        stmt = select(FacultyAssignment.id).where(
            FacultyAssignment.faculty_id == faculty_id,
            FacultyAssignment.subject_id == subject_id,
            FacultyAssignment.academic_class_id == class_id,
        )
        return db.execute(stmt).first() is not None

    def external_id_exists(self, db: Session, external_id: str) -> bool:
        stmt = select(AttendanceSession.id).where(AttendanceSession.external_session_id == external_id)
        return db.execute(stmt).first() is not None

    def add_session(self, db: Session, session: AttendanceSession) -> AttendanceSession:
        db.add(session)
        db.flush()
        return session

    def get_session(self, db: Session, session_id: int, *, for_update: bool = False) -> AttendanceSession | None:
        stmt = select(AttendanceSession).where(AttendanceSession.id == session_id)
        if for_update:
            # Lock only the session row (eager joins are avoided so FOR UPDATE is valid on PostgreSQL).
            stmt = stmt.with_for_update(of=AttendanceSession)
        else:
            stmt = stmt.options(*_SESSION_LOAD)
        return db.execute(stmt).scalar_one_or_none()

    def session_records(self, db: Session, session_id: int) -> list[AttendanceRecord]:
        stmt = (
            select(AttendanceRecord)
            .options(joinedload(AttendanceRecord.student))
            .where(AttendanceRecord.session_id == session_id)
            .order_by(AttendanceRecord.student_id)
        )
        return list(db.execute(stmt).scalars())

    def add_records(self, db: Session, records: list[AttendanceRecord]) -> None:
        db.add_all(records)
        db.flush()

    def list_sessions(
        self, db: Session, f: AttendanceFilters, params: PageParams, statuses: list[SessionStatus] | None = None
    ):
        """Sessions with present/total counts. Returns (rows[(session, present, total)], total_rows)."""
        present_sq = (
            select(func.count(AttendanceRecord.id))
            .where(AttendanceRecord.session_id == AttendanceSession.id,
                   AttendanceRecord.status == AttendanceStatus.PRESENT)
            .correlate(AttendanceSession).scalar_subquery()
        )
        total_sq = (
            select(func.count(AttendanceRecord.id))
            .where(AttendanceRecord.session_id == AttendanceSession.id)
            .correlate(AttendanceSession).scalar_subquery()
        )
        stmt = (
            select(AttendanceSession, present_sq.label("present"), total_sq.label("total"))
            .join(AcademicClass, AcademicClass.id == AttendanceSession.academic_class_id)
            .options(*_SESSION_LOAD)
            .order_by(AttendanceSession.date.desc(), AttendanceSession.id.desc())
        )
        if statuses:
            stmt = stmt.where(AttendanceSession.status.in_(statuses))
        stmt = _apply_session_filters(stmt, f)
        return paginate(db, stmt, params, scalars=False)

    # ---- aggregates (submitted sessions only) -----------------------------
    def _record_query(self, columns, f: AttendanceFilters):
        stmt = (
            select(*columns)
            .select_from(AttendanceRecord)
            .join(AttendanceSession, AttendanceSession.id == AttendanceRecord.session_id)
            .join(AcademicClass, AcademicClass.id == AttendanceSession.academic_class_id)
            .join(Department, Department.id == AcademicClass.department_id)
            .join(Subject, Subject.id == AttendanceSession.subject_id)
            .join(Student, Student.id == AttendanceRecord.student_id)
            .where(AttendanceSession.status == SessionStatus.SUBMITTED)
        )
        stmt = _apply_session_filters(stmt, f)
        if f.student_id is not None:
            stmt = stmt.where(AttendanceRecord.student_id == f.student_id)
        return stmt

    def totals(self, db: Session, f: AttendanceFilters) -> tuple[int, int]:
        row = db.execute(self._record_query([_TOTAL, _PRESENT], f)).one()
        return int(row[0] or 0), int(row[1] or 0)

    def grouped(self, db: Session, f: AttendanceFilters, *group_cols):
        """Rows of (*group_cols, total, present)."""
        stmt = self._record_query([*group_cols, _TOTAL, _PRESENT], f).group_by(*group_cols).order_by(*group_cols)
        return db.execute(stmt).all()

    def low_attendance(self, db: Session, f: AttendanceFilters, threshold: float, limit: int = 100):
        cols = [Student.id, Student.student_id, Student.name, Department.code, Student.semester, Student.section]
        stmt = (
            self._record_query([*cols, _TOTAL, _PRESENT], f)
            .group_by(*cols)
            .having(_PRESENT * 100.0 < threshold * _TOTAL)
            .order_by((_PRESENT * 100.0 / _TOTAL).asc(), Student.student_id)
            .limit(limit)
        )
        return db.execute(stmt).all()

    def low_attendance_count(self, db: Session, f: AttendanceFilters, threshold: float) -> int:
        inner = (
            self._record_query([Student.id], f)
            .group_by(Student.id)
            .having(_PRESENT * 100.0 < threshold * _TOTAL)
            .subquery()
        )
        return int(db.execute(select(func.count()).select_from(inner)).scalar_one())

    def student_subject_rows(self, db: Session, f: AttendanceFilters):
        """Per (student, subject) totals for reports."""
        cols = [Student.student_id, Student.name, Department.code, Student.semester, Student.section,
                Subject.code, Subject.name]
        stmt = (
            self._record_query([*cols, _TOTAL, _PRESENT], f)
            .group_by(*cols)
            .order_by(Student.student_id, Subject.code)
        )
        return stmt


attendance_repo = AttendanceRepository()

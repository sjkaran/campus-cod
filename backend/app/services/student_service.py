from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Role, Student, Subject, User
from app.repositories.attendance_repository import AttendanceFilters, attendance_repo
from app.repositories.student_repository import StudentFilters, student_repo
from app.repositories.user_repository import user_repo
from app.schemas.student import StudentAttendanceResponse, SubjectAttendance
from app.services.access import narrow_department, resolve_scope
from app.utils.calculations import summarize
from app.utils.pagination import PageParams


def list_students(
    db: Session, user: User, *, department: str | None, semester: int | None,
    section: str | None, q: str | None, params: PageParams,
):
    scope = resolve_scope(db, user)  # ADMIN or HOD (route-enforced); HOD is pinned to own department
    dept_id = narrow_department(db, scope, department)
    return student_repo.list(db, StudentFilters(dept_id, semester, section, q), params)


def get_student(db: Session, user: User, pk: int) -> Student:
    student = student_repo.get(db, pk)
    allowed = False
    if student is not None:
        if user.role == Role.ADMIN:
            allowed = True
        elif user.role == Role.HOD:
            hod = user_repo.hod_for_user(db, user.id)
            allowed = bool(hod and hod.department_id == student.department_id)
        elif user.role == Role.STUDENT:
            allowed = student.user_id == user.id
    if not allowed:
        # Same response whether it doesn't exist or isn't yours: no ID enumeration.
        raise NotFoundError("Student not found")
    return student


def my_attendance(db: Session, student: Student) -> StudentAttendanceResponse:
    f = AttendanceFilters(student_id=student.id)
    overall = summarize(*attendance_repo.totals(db, f))
    rows = attendance_repo.grouped(db, f, Subject.id, Subject.code, Subject.name)
    subjects = [
        SubjectAttendance(subject_id=sid, subject_code=code, subject_name=name, **summarize(total, present).model_dump())
        for sid, code, name, total, present in rows
    ]
    return StudentAttendanceResponse(overall=overall, subjects=subjects)

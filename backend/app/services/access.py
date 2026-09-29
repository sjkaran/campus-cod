"""Server-side data-scope resolution: who may see which slice of data."""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models import Role, User
from app.repositories.catalog_repository import catalog_repo
from app.repositories.user_repository import user_repo


@dataclass(frozen=True)
class Scope:
    role: Role
    department_id: int | None = None  # HOD: fixed to own department. ADMIN: None (institution-wide)
    faculty_id: int | None = None     # FACULTY: only their own sessions


def resolve_scope(db: Session, user: User) -> Scope:
    if user.role == Role.ADMIN:
        return Scope(role=Role.ADMIN)
    if user.role == Role.HOD:
        hod = user_repo.hod_for_user(db, user.id)
        if not hod:
            raise ForbiddenError("HOD profile not found")
        return Scope(role=Role.HOD, department_id=hod.department_id)
    if user.role == Role.FACULTY:
        fac = user_repo.faculty_for_user(db, user.id)
        if not fac:
            raise ForbiddenError("Faculty profile not found")
        return Scope(role=Role.FACULTY, faculty_id=fac.id)
    raise ForbiddenError()


def narrow_department(db: Session, scope: Scope, department_code: str | None) -> int | None:
    """Apply a client-requested department filter WITHOUT letting it widen the caller's scope."""
    if not department_code:
        return scope.department_id
    dept = catalog_repo.department_by_code(db, department_code)
    if dept is None:
        raise NotFoundError("Department not found")
    if scope.role == Role.HOD and dept.id != scope.department_id:
        raise ForbiddenError("You may only access data for your own department")
    return dept.id


def resolve_subject_id(db: Session, subject_code: str | None) -> int | None:
    if not subject_code:
        return None
    subject = catalog_repo.subject_by_code(db, subject_code)
    if subject is None:
        raise NotFoundError("Subject not found")
    return subject.id

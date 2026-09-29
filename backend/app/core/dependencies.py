"""FastAPI dependencies: authentication and role-based access control (RBAC).

Every role check happens HERE, on the server, independently of what any client UI shows.
"""
from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.database import get_db
from app.models import Faculty, Hod, Role, Student, User
from app.repositories.user_repository import user_repo

bearer_scheme = HTTPBearer(auto_error=False, description="JWT from POST /api/auth/login")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)
) -> User:
    if creds is None:
        raise UnauthorizedError("Not authenticated")
    payload = decode_access_token(creds.credentials)
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        raise UnauthorizedError("Invalid token")
    user = user_repo.get(db, user_id)
    # The database is the authority: a deactivated user or changed role invalidates old tokens.
    if user is None or not user.is_active or payload.get("role") != user.role.value:
        raise UnauthorizedError("Invalid or expired token")
    return user


def require_roles(*roles: Role) -> Callable[..., User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError()
        return user

    return dependency


require_student = require_roles(Role.STUDENT)
require_faculty = require_roles(Role.FACULTY)
require_hod = require_roles(Role.HOD)
require_admin = require_roles(Role.ADMIN)


def current_student(user: User = Depends(require_student), db: Session = Depends(get_db)) -> Student:
    student = user_repo.student_for_user(db, user.id)
    if student is None:
        raise ForbiddenError("Student profile not found")
    return student


def current_faculty(user: User = Depends(require_faculty), db: Session = Depends(get_db)) -> Faculty:
    faculty = user_repo.faculty_for_user(db, user.id)
    if faculty is None:
        raise ForbiddenError("Faculty profile not found")
    return faculty


def current_hod(user: User = Depends(require_hod), db: Session = Depends(get_db)) -> Hod:
    hod = user_repo.hod_for_user(db, user.id)
    if hod is None:
        raise ForbiddenError("HOD profile not found")
    return hod

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models import Role, User
from app.repositories.user_repository import user_repo
from app.schemas.auth import LoginResponse, UserBrief
from app.services import audit_service

log = logging.getLogger("app.auth")


def user_brief(db: Session, user: User) -> UserBrief:
    profile = None
    if user.role == Role.STUDENT:
        profile = user_repo.student_for_user(db, user.id)
    elif user.role == Role.FACULTY:
        profile = user_repo.faculty_for_user(db, user.id)
    elif user.role == Role.HOD:
        profile = user_repo.hod_for_user(db, user.id)
    elif user.role == Role.ADMIN:
        profile = user_repo.admin_for_user(db, user.id)
    return UserBrief(
        id=user.id, username=user.username, role=user.role,
        name=getattr(profile, "name", None),
        department_code=getattr(profile, "department_code", None) if profile and hasattr(profile, "department_id") else None,
    )


def login(db: Session, username: str, password: str) -> LoginResponse:
    user = user_repo.get_by_username(db, username)
    # Always run a hash verification (dummy hash if user is unknown) to keep timing similar.
    valid = verify_password(password, user.password_hash if user else None)
    if not user or not valid:
        log.warning("login_failed username=%s", username[:64])
        raise UnauthorizedError("Incorrect username or password")
    if not user.is_active:
        log.warning("login_blocked_inactive user_id=%s", user.id)
        raise ForbiddenError("This account has been disabled")

    user.last_login = datetime.now(timezone.utc)
    audit_service.record(db, user_id=user.id, action="LOGIN", resource_type="user", resource_id=user.id)
    db.commit()

    token, expires_in = create_access_token(user.id, user.role.value)
    log.info("login_ok user_id=%s role=%s", user.id, user.role.value)
    return LoginResponse(access_token=token, expires_in=expires_in, user=user_brief(db, user))

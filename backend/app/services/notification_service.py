import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models import (
    AudienceType, Hod, Notification, NotificationTarget, Role, Student, User,
)
from app.repositories.catalog_repository import catalog_repo
from app.repositories.notification_repository import notification_repo
from app.repositories.student_repository import student_repo
from app.repositories.user_repository import user_repo
from app.schemas.notification import (
    NotificationCreate, NotificationDetail, NotificationResponse, ReadResult,
)
from app.services import audit_service
from app.utils.pagination import PageParams

log = logging.getLogger("app.notifications")


def _resolve_targets(db: Session, data: NotificationCreate, hod: Hod | None) -> list[NotificationTarget]:
    out: list[NotificationTarget] = []
    for t in data.targets:
        dept_id = None
        if t.department_code:
            dept = catalog_repo.department_by_code(db, t.department_code)
            if dept is None:
                raise BadRequestError(f"Unknown department '{t.department_code}'")
            dept_id = dept.id
        student_pk = student_dept = None
        if t.student_id:
            found = student_repo.get_by_public_ids(db, [t.student_id])
            if not found:
                raise BadRequestError(f"Unknown student '{t.student_id}'")
            student_pk, student_dept = found[0].id, found[0].department_id
        if hod is not None:  # HOD authority is confined to their own department
            dept_id = dept_id or hod.department_id
            if dept_id != hod.department_id or (student_dept and student_dept != hod.department_id):
                raise ForbiddenError("HODs can only target their own department")
        out.append(NotificationTarget(
            department_id=dept_id, semester=t.semester,
            section=t.section.strip().upper() if t.section else None, student_id=student_pk,
        ))
    return out


def _validate_audience(audience: AudienceType, targets: list[NotificationTarget]) -> None:
    if audience == AudienceType.ALL_STUDENTS:
        if targets:
            raise BadRequestError("ALL_STUDENTS notifications must not have targets")
        return
    if not targets:
        raise BadRequestError(f"{audience.value} notifications require at least one target")
    for t in targets:
        if t.department_id is None and t.semester is None and t.section is None and t.student_id is None:
            raise BadRequestError("Each target must specify at least one criterion")
        if audience == AudienceType.DEPARTMENT and t.department_id is None:
            raise BadRequestError("DEPARTMENT targets require department_code")
        if audience == AudienceType.SEMESTER and t.semester is None:
            raise BadRequestError("SEMESTER targets require semester")
        if audience == AudienceType.SECTION and (t.department_id is None or t.semester is None or not t.section):
            raise BadRequestError("SECTION targets require department_code, semester and section")


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def publish(db: Session, user: User, data: NotificationCreate) -> NotificationDetail:
    hod = None
    if user.role == Role.HOD:
        hod = user_repo.hod_for_user(db, user.id)
        if hod is None:
            raise ForbiddenError("HOD profile not found")
        if data.audience_type == AudienceType.ALL_STUDENTS:
            raise ForbiddenError("HODs cannot publish institution-wide notifications")
    if data.expires_at and _aware(data.expires_at) <= datetime.now(timezone.utc):
        raise BadRequestError("expires_at must be in the future")

    targets = _resolve_targets(db, data, hod)
    _validate_audience(data.audience_type, targets)

    n = Notification(
        title=data.title.strip(), message=data.message.strip(), created_by=user.id, priority=data.priority,
        audience_type=data.audience_type, expires_at=data.expires_at, targets=targets,
    )
    notification_repo.add(db, n)
    audit_service.record(db, user_id=user.id, action="NOTIFICATION_PUBLISHED", resource_type="notification",
                         resource_id=n.id, meta={"audience": data.audience_type.value})
    db.commit()
    log.info("notification_published id=%s by=%s", n.id, user.id)
    return get_detail(db, n.id)


def get_detail(db: Session, notification_id: int) -> NotificationDetail:
    n = notification_repo.get(db, notification_id)
    if n is None:
        raise NotFoundError("Notification not found")
    names = user_repo.display_names(db, [n.created_by])
    return NotificationDetail.model_validate(n).model_copy(update={"author_name": names.get(n.created_by)})


def list_for_student(db: Session, student: Student, unread: bool | None, params: PageParams):
    rows, total = notification_repo.list_for_student(db, student, params, unread)
    names = user_repo.display_names(db, list({n.created_by for n, _ in rows}))
    items = [
        NotificationResponse.model_validate(n).model_copy(
            update={"author_name": names.get(n.created_by), "is_read": read_at is not None}
        )
        for n, read_at in rows
    ]
    return items, total


def list_published(db: Session, user: User, params: PageParams, *, only_mine: bool):
    """ADMIN sees everything (unless only_mine); HOD only ever sees their own."""
    created_by = user.id if (only_mine or user.role == Role.HOD) else None
    rows, total = notification_repo.list_all(db, params, created_by=created_by)
    names = user_repo.display_names(db, list({n.created_by for n in rows}))
    return [NotificationResponse.model_validate(n).model_copy(update={"author_name": names.get(n.created_by)}) for n in rows], total


def mark_read(db: Session, student: Student, notification_id: int) -> ReadResult:
    if not notification_repo.is_visible_to(db, notification_id, student):
        raise NotFoundError("Notification not found")
    notification_repo.mark_read(db, notification_id, student.id)
    db.commit()
    return ReadResult(notification_id=notification_id, is_read=True)

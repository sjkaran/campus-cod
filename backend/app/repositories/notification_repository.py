from datetime import datetime, timezone

from sqlalchemy import and_, exists, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AudienceType, Notification, NotificationRead, NotificationStatus, NotificationTarget, Student,
)
from app.utils.pagination import PageParams, paginate


def _visible_to(student: Student):
    """SQL predicate: notification is active, unexpired, and targets this student."""
    now = datetime.now(timezone.utc)
    t = NotificationTarget
    matches_target = exists().where(
        t.notification_id == Notification.id,
        or_(t.department_id.is_(None), t.department_id == student.department_id),
        or_(t.semester.is_(None), t.semester == student.semester),
        or_(t.section.is_(None), t.section == student.section),
        or_(t.student_id.is_(None), t.student_id == student.id),
    )
    return and_(
        Notification.status == NotificationStatus.ACTIVE,
        or_(Notification.expires_at.is_(None), Notification.expires_at > now),
        or_(Notification.audience_type == AudienceType.ALL_STUDENTS, matches_target),
    )


class NotificationRepository:
    def add(self, db: Session, n: Notification) -> Notification:
        db.add(n)
        db.flush()
        return n

    def get(self, db: Session, notification_id: int) -> Notification | None:
        stmt = (
            select(Notification)
            .options(joinedload(Notification.author), joinedload(Notification.targets))
            .where(Notification.id == notification_id)
        )
        return db.execute(stmt).unique().scalar_one_or_none()

    def list_for_student(self, db: Session, student: Student, params: PageParams, unread: bool | None):
        stmt = (
            select(Notification, NotificationRead.read_at)
            .outerjoin(
                NotificationRead,
                and_(NotificationRead.notification_id == Notification.id, NotificationRead.student_id == student.id),
            )
            .options(joinedload(Notification.author))
            .where(_visible_to(student))
            .order_by(Notification.created_at.desc(), Notification.id.desc())
        )
        if unread is True:
            stmt = stmt.where(NotificationRead.read_at.is_(None))
        elif unread is False:
            stmt = stmt.where(NotificationRead.read_at.is_not(None))
        return paginate(db, stmt, params, scalars=False)

    def is_visible_to(self, db: Session, notification_id: int, student: Student) -> bool:
        stmt = select(Notification.id).where(Notification.id == notification_id, _visible_to(student))
        return db.execute(stmt).first() is not None

    def mark_read(self, db: Session, notification_id: int, student_id: int) -> None:
        if db.get(NotificationRead, (notification_id, student_id)) is None:
            db.add(NotificationRead(notification_id=notification_id, student_id=student_id))
            db.flush()

    def list_all(self, db: Session, params: PageParams, created_by: int | None = None):
        stmt = (
            select(Notification)
            .options(joinedload(Notification.author))
            .order_by(Notification.created_at.desc(), Notification.id.desc())
        )
        if created_by is not None:
            stmt = stmt.where(Notification.created_by == created_by)
        return paginate(db, stmt, params)


notification_repo = NotificationRepository()

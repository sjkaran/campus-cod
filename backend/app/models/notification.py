from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, enum_col, utcnow
from app.models.enums import AudienceType, NotificationStatus, Priority


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    priority: Mapped[Priority] = mapped_column(enum_col(Priority), default=Priority.NORMAL)
    audience_type: Mapped[AudienceType] = mapped_column(enum_col(AudienceType))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[NotificationStatus] = mapped_column(enum_col(NotificationStatus), default=NotificationStatus.ACTIVE)

    author = relationship("User")
    targets = relationship("NotificationTarget", back_populates="notification", cascade="all, delete-orphan")


class NotificationTarget(Base):
    """One targeting rule. A student matches if every NON-NULL field equals the student's value.

    ALL_STUDENTS notifications have no target rows.
    """

    __tablename__ = "notification_targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"), index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    semester: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(8), nullable=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)

    notification = relationship("Notification", back_populates="targets")
    department = relationship("Department")


class NotificationRead(Base):
    __tablename__ = "notification_reads"

    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True, index=True)
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

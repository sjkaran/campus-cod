import datetime as dt
from datetime import datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, enum_col, utcnow
from app.models.enums import AttendanceStatus, SessionStatus


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ID assigned by the external QR system (idempotency key for imports).
    external_session_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    academic_class_id: Mapped[int] = mapped_column(ForeignKey("academic_classes.id"), index=True)
    # NB: annotated via `dt.date` because this attribute is itself named `date` and would shadow the type.
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[SessionStatus] = mapped_column(enum_col(SessionStatus), default=SessionStatus.DRAFT, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    faculty = relationship("Faculty")
    subject = relationship("Subject")
    academic_class = relationship("AcademicClass")
    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

    @property
    def subject_code(self) -> str:
        return self.subject.code

    @property
    def subject_name(self) -> str:
        return self.subject.name

    @property
    def faculty_name(self) -> str:
        return self.faculty.name

    @property
    def class_label(self) -> str:
        return self.academic_class.label


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"),
        Index("ix_attendance_records_student_session", "student_id", "session_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("attendance_sessions.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    status: Mapped[AttendanceStatus] = mapped_column(enum_col(AttendanceStatus))
    marked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student")

    @property
    def student_public_id(self) -> str:
        return self.student.student_id

    @property
    def student_name(self) -> str:
        return self.student.name

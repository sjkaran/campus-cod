from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, enum_col
from app.models.enums import RecordStatus


class Faculty(Base, TimestampMixin):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    faculty_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    status: Mapped[RecordStatus] = mapped_column(enum_col(RecordStatus), default=RecordStatus.ACTIVE)

    user = relationship("User")
    department = relationship("Department")
    assignments = relationship("FacultyAssignment", back_populates="faculty", cascade="all, delete-orphan")

    @property
    def department_code(self) -> str:
        return self.department.code


class FacultyAssignment(Base):
    """Which faculty teaches which subject to which class. Gates session creation."""

    __tablename__ = "faculty_assignments"
    __table_args__ = (UniqueConstraint("faculty_id", "subject_id", "academic_class_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    academic_class_id: Mapped[int] = mapped_column(ForeignKey("academic_classes.id"))

    faculty = relationship("Faculty", back_populates="assignments")
    subject = relationship("Subject")
    academic_class = relationship("AcademicClass")

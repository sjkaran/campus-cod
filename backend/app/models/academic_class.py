from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, enum_col
from app.models.enums import RecordStatus


class AcademicClass(Base):
    """A cohort: e.g. CSE / Semester 6 / Section A / 2026-27."""

    __tablename__ = "academic_classes"
    __table_args__ = (UniqueConstraint("department_id", "semester", "section", "academic_year"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    semester: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(8))
    academic_year: Mapped[str] = mapped_column(String(9))  # "2026-27"
    status: Mapped[RecordStatus] = mapped_column(enum_col(RecordStatus), default=RecordStatus.ACTIVE)

    department = relationship("Department")

    @property
    def department_code(self) -> str:
        return self.department.code

    @property
    def label(self) -> str:
        return f"{self.department.code} Sem {self.semester} Sec {self.section} ({self.academic_year})"

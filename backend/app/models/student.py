from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, enum_col
from app.models.enums import RecordStatus


class Student(Base, TimestampMixin):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("semester BETWEEN 1 AND 12", name="ck_students_semester"),
        Index("ix_students_dept_sem_sec", "department_id", "semester", "section"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    student_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # public ID, e.g. "S2026001"
    roll_number: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    semester: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(8))
    status: Mapped[RecordStatus] = mapped_column(enum_col(RecordStatus), default=RecordStatus.ACTIVE)

    user = relationship("User")
    department = relationship("Department")

    @property
    def department_code(self) -> str:
        return self.department.code

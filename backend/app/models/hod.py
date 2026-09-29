from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Hod(Base, TimestampMixin):
    __tablename__ = "hods"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    employee_id: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    # One HOD per department; HOD authority is scoped to this department.
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), unique=True)

    user = relationship("User")
    department = relationship("Department")

    @property
    def department_code(self) -> str:
        return self.department.code

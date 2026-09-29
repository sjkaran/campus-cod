from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, enum_col
from app.models.enums import RecordStatus


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    credits: Mapped[int] = mapped_column(Integer, default=3)
    status: Mapped[RecordStatus] = mapped_column(enum_col(RecordStatus), default=RecordStatus.ACTIVE)

    department = relationship("Department")

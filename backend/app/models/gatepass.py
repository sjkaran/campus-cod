from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, enum_col, utcnow
from app.models.enums import GatePassStatus


class GatePass(Base):
    __tablename__ = "gate_passes"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    destination: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(Text)
    departure_date: Mapped[date] = mapped_column(Date)
    departure_time: Mapped[time] = mapped_column(Time)
    return_date: Mapped[date] = mapped_column(Date)
    return_time: Mapped[time] = mapped_column(Time)
    status: Mapped[GatePassStatus] = mapped_column(
        enum_col(GatePassStatus), default=GatePassStatus.PENDING, index=True
    )
    hod_id: Mapped[int | None] = mapped_column(ForeignKey("hods.id"), nullable=True)
    hod_remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student = relationship("Student")
    hod = relationship("Hod")

    @property
    def student_public_id(self) -> str:
        return self.student.student_id

    @property
    def student_name(self) -> str:
        return self.student.name

    @property
    def department_code(self) -> str:
        return self.student.department.code

    @property
    def hod_name(self) -> str | None:
        return self.hod.name if self.hod else None

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, enum_col
from app.models.enums import RecordStatus


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[RecordStatus] = mapped_column(enum_col(RecordStatus), default=RecordStatus.ACTIVE)

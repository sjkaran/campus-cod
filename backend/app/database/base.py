from datetime import datetime, timezone
import enum

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


def enum_col(enum_cls: type[enum.Enum]) -> Enum:
    """Portable enum column (VARCHAR + validation, no native PG enum => easy migrations)."""
    return Enum(enum_cls, native_enum=False, length=24, validate_strings=True)

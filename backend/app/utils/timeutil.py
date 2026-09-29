from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.core.config import settings


def campus_now() -> datetime:
    """Current wall-clock time in the campus timezone, naive (for comparing with date+time inputs)."""
    return datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)


def combine(d: date, t: time) -> datetime:
    return datetime.combine(d, t)

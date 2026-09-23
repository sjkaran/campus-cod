"""Small shared helpers used across UI modules."""

from datetime import datetime

from config.settings import ATTENDANCE_GOOD_THRESHOLD, ATTENDANCE_NORMAL_THRESHOLD


def attendance_band(percentage: float) -> str:
    """Returns 'good' | 'normal' | 'attention' for a given percentage."""
    if percentage >= ATTENDANCE_GOOD_THRESHOLD:
        return "good"
    if percentage >= ATTENDANCE_NORMAL_THRESHOLD:
        return "normal"
    return "attention"


def attendance_label(percentage: float) -> str:
    return {"good": "Good", "normal": "Normal", "attention": "Attention"}[
        attendance_band(percentage)
    ]


def is_valid_date(value: str, fmt: str = "%Y-%m-%d") -> bool:
    try:
        datetime.strptime(value, fmt)
        return True
    except (ValueError, TypeError):
        return False


def today_str(fmt: str = "%Y-%m-%d") -> str:
    return datetime.now().strftime(fmt)


def truncate(text: str, length: int = 40) -> str:
    text = text or ""
    return text if len(text) <= length else text[: length - 1] + "…"

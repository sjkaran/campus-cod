"""Small generic helpers shared across services/UI."""

from datetime import datetime, timedelta
import random
import string


def new_id(prefix: str) -> str:
    """Generates a short pseudo-unique id, e.g. N-7F3K9A. Stage 1 only —
    the backend will assign authoritative IDs in Stage 2."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


def now_str(fmt: str = "%Y-%m-%d %H:%M") -> str:
    return datetime.now().strftime(fmt)


def today_str(fmt: str = "%Y-%m-%d") -> str:
    return datetime.now().strftime(fmt)


def days_from_today(offset: int, fmt: str = "%Y-%m-%d") -> str:
    return (datetime.now() + timedelta(days=offset)).strftime(fmt)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default

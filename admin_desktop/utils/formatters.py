"""Display-formatting helpers (numbers, percentages, dates, status text)."""

from datetime import datetime


def format_percentage(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def format_number(value: int) -> str:
    return f"{value:,}"


def format_date_display(value: str, in_fmt: str = "%Y-%m-%d", out_fmt: str = "%d %b %Y") -> str:
    if not value:
        return "—"
    try:
        return datetime.strptime(value, in_fmt).strftime(out_fmt)
    except ValueError:
        return value


def format_datetime_display(value: str, in_fmt: str = "%Y-%m-%d %H:%M", out_fmt: str = "%d %b %Y, %I:%M %p") -> str:
    if not value:
        return "—"
    try:
        return datetime.strptime(value, in_fmt).strftime(out_fmt)
    except ValueError:
        return value


def status_label(status: str) -> str:
    """Title-cases status codes like ACTIVE -> Active for display."""
    return status.replace("_", " ").title() if status else "—"


def truncate(text: str, max_len: int = 60) -> str:
    if not text:
        return ""
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"

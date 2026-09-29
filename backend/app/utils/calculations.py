"""Single source of truth for derived numbers. Clients must never recompute these."""
from app.schemas.student import AttendanceSummary


def percentage(present: int, total: int) -> float:
    return round(present * 100.0 / total, 2) if total else 0.0


def summarize(total: int, present: int) -> AttendanceSummary:
    total, present = int(total or 0), int(present or 0)
    return AttendanceSummary(
        total_classes=total, present=present, absent=total - present, percentage=percentage(present, total)
    )

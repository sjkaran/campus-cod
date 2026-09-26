"""Data model for campus notifications published by the Admin."""

from dataclasses import dataclass, field


@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    audience: str          # ALL_STUDENTS | DEPARTMENT | SEMESTER | SECTION | GROUP
    audience_detail: str    # e.g. "Computer Science" when audience is scoped
    priority: str           # NORMAL | IMPORTANT | URGENT
    published_by: str
    published_date: str
    expiration_date: str
    status: str             # ACTIVE | EXPIRED | DRAFT
    recipient_count: int = 0

"""Notification model."""

from dataclasses import dataclass


class NotificationStatus:
    PUBLISHED = "PUBLISHED"
    EXPIRED = "EXPIRED"


@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    audience: str
    priority: str
    expiration_date: str
    created_at: str
    status: str = NotificationStatus.PUBLISHED

    @staticmethod
    def from_dict(data: dict) -> "Notification":
        return Notification(**data)

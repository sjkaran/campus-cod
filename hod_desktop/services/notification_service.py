"""Notification service — API boundary for publishing/listing notices."""

from models.notification import Notification
from mock import mock_data

VALID_AUDIENCES = ["Department", "All Students", "Specific group"]
VALID_PRIORITIES = ["Normal", "High", "Urgent"]


def get_my_notifications() -> list[Notification]:
    """Future API: GET /api/notifications/created-by-me"""
    return [Notification.from_dict(n) for n in mock_data.MOCK_NOTIFICATIONS]


def publish_notification(title, message, audience, priority, expiration_date) -> Notification:
    """
    Future API: POST /api/notifications

    Raises ValueError on invalid input — caller (ui/notifications.py)
    surfaces this as inline form validation.
    """
    title = (title or "").strip()
    message = (message or "").strip()

    if not title:
        raise ValueError("Notification title is required.")
    if not message:
        raise ValueError("Notification message is required.")
    if audience not in VALID_AUDIENCES:
        raise ValueError("Please select a valid audience.")
    if priority not in VALID_PRIORITIES:
        raise ValueError("Please select a valid priority.")
    if not expiration_date:
        raise ValueError("Expiration date is required.")

    record = mock_data.add_notification_record(
        title, message, audience, priority, expiration_date
    )
    return Notification.from_dict(record)

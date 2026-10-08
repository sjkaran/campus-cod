"""Notification service — API boundary for publishing/listing notices."""

from config.settings import DATA_SOURCE_MODE
from models.notification import Notification
from mock import mock_data

VALID_AUDIENCES = ["Department", "All Students", "Specific group"]
VALID_PRIORITIES = ["Normal", "High", "Urgent"]

# Map UI audience labels to backend AudienceType enum values
_AUDIENCE_MAP = {
    "Department": "DEPARTMENT",
    "All Students": "ALL",
    "Specific group": "TARGETED",
}

# Map UI priority labels to backend Priority enum values
_PRIORITY_MAP = {
    "Normal": "NORMAL",
    "High": "HIGH",
    "Urgent": "URGENT",
}


def _to_notification_dict(r: dict) -> dict:
    """Map a backend notification response to the fields Notification expects."""
    # Map backend audience_type back to UI label
    audience_type = r.get("audience_type", "ALL")
    audience = next(
        (k for k, v in _AUDIENCE_MAP.items() if v == audience_type),
        audience_type,
    )
    priority_val = r.get("priority", "NORMAL")
    priority = next(
        (k for k, v in _PRIORITY_MAP.items() if v == priority_val),
        priority_val,
    )
    expires_at = r.get("expires_at") or ""
    if expires_at and "T" in expires_at:
        expires_at = expires_at[:10]
    created_at = str(r.get("created_at", ""))
    return {
        "notification_id": str(r.get("id", "")),
        "title": r.get("title", ""),
        "message": r.get("message", ""),
        "audience": audience,
        "priority": priority,
        "expiration_date": expires_at,
        "created_at": created_at,
        "status": r.get("status", "PUBLISHED"),
    }


def get_my_notifications() -> list[Notification]:
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            rows = api_client.get_my_notifications()
            return [Notification.from_dict(_to_notification_dict(r)) for r in rows]
        except ApiClientError as e:
            raise RuntimeError(str(e))
    return [Notification.from_dict(n) for n in mock_data.MOCK_NOTIFICATIONS]


def publish_notification(title, message, audience, priority, expiration_date) -> Notification:
    """
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

    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        payload = {
            "title": title,
            "message": message,
            "audience_type": _AUDIENCE_MAP[audience],
            "priority": _PRIORITY_MAP[priority],
            "expires_at": f"{expiration_date}T23:59:59",
        }
        try:
            response = api_client.publish_notification(payload)
            data = response.get("data", response)
            return Notification.from_dict(_to_notification_dict(data))
        except ApiClientError as e:
            raise RuntimeError(str(e))

    record = mock_data.add_notification_record(
        title, message, audience, priority, expiration_date
    )
    return Notification.from_dict(record)

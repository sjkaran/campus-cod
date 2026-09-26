"""
Notification service.

Stage 1: getNotifications()/publishNotification() -> mock.notifications
Stage 2: -> ApiClient -> GET /api/notifications/admin, POST /api/notifications
"""

from models.notification import Notification
from mock.notifications import get_all_notifications, add_notification, audience_label
from mock.students import DEPARTMENTS


def get_audience_options() -> list[tuple[str, str]]:
    """Returns (code, label) pairs for the audience dropdown."""
    return [
        ("ALL_STUDENTS", "All Students"),
        ("DEPARTMENT", "Department"),
        ("SEMESTER", "Semester"),
        ("SECTION", "Section"),
        ("GROUP", "Specific Student Group"),
    ]


def get_priority_options() -> list[str]:
    return ["Normal", "Important", "Urgent"]


def get_notifications(search: str = "", priority: str = "All", status: str = "All",
                       audience: str = "All") -> list[Notification]:
    """FUTURE API INTEGRATION: GET /api/notifications/admin?search=&priority=&status=&audience="""
    notifications = get_all_notifications()
    search = (search or "").strip().lower()

    def matches(n: Notification) -> bool:
        if priority != "All" and n.priority != priority.upper():
            return False
        if status != "All" and n.status != status.upper():
            return False
        if audience != "All" and n.audience != audience:
            return False
        if search and search not in n.title.lower() and search not in n.message.lower():
            return False
        return True

    return [n for n in notifications if matches(n)]


def publish_notification(title: str, message: str, audience_code: str, audience_detail: str,
                          priority: str, expiration_date: str, published_by: str = "Admin") -> Notification:
    """FUTURE API INTEGRATION: POST /api/notifications"""
    return add_notification(
        title=title,
        message=message,
        audience=audience_code,
        audience_detail=audience_detail,
        priority=priority.upper(),
        expiration_date=expiration_date,
        published_by=published_by,
    )


def estimate_audience_size(audience_code: str, audience_detail: str) -> int:
    from mock.notifications import _estimate_recipients  # internal reuse, mock-layer only
    return _estimate_recipients(audience_code, audience_detail)

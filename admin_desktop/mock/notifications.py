"""
Mock notification dataset.

FUTURE API INTEGRATION
Replace this module's data source with:
    GET /api/notifications/admin
    POST /api/notifications
"""

from models.notification import Notification
from utils.helpers import days_from_today, new_id
from mock.students import get_all_students

_SEED_NOTIFICATIONS = [
    dict(title="Semester Examination Schedule", message="The Semester End Examination timetable has been published on the portal. Students are advised to check their respective slots.",
         audience="ALL_STUDENTS", audience_detail="All Students", priority="IMPORTANT",
         published_offset=-9, expiration_offset=20, status="ACTIVE"),
    dict(title="Campus Wi-Fi Maintenance", message="Campus Wi-Fi services will be temporarily unavailable between 1 AM and 4 AM for scheduled maintenance.",
         audience="ALL_STUDENTS", audience_detail="All Students", priority="NORMAL",
         published_offset=-2, expiration_offset=1, status="ACTIVE"),
    dict(title="CSE Department Workshop on AI", message="A two-day workshop on Applied AI will be conducted for Computer Science students in the seminar hall.",
         audience="DEPARTMENT", audience_detail="Computer Science", priority="NORMAL",
         published_offset=-5, expiration_offset=10, status="ACTIVE"),
    dict(title="Urgent: Fee Payment Deadline Extended", message="Due to portal downtime, the semester fee payment deadline has been extended by 5 days.",
         audience="ALL_STUDENTS", audience_detail="All Students", priority="URGENT",
         published_offset=-1, expiration_offset=5, status="ACTIVE"),
    dict(title="6th Semester Project Submission Guidelines", message="Guidelines for final project submission have been shared. Please review the format and deadlines carefully.",
         audience="SEMESTER", audience_detail="Semester 6", priority="IMPORTANT",
         published_offset=-14, expiration_offset=-1, status="EXPIRED"),
    dict(title="Placement Drive: TechNova Solutions", message="TechNova Solutions will be conducting a placement drive for eligible final-year students next week.",
         audience="SEMESTER", audience_detail="Semester 8", priority="IMPORTANT",
         published_offset=-3, expiration_offset=7, status="ACTIVE"),
    dict(title="Library Extended Hours During Exams", message="The central library will remain open until midnight during the examination period.",
         audience="ALL_STUDENTS", audience_detail="All Students", priority="NORMAL",
         published_offset=-20, expiration_offset=-10, status="EXPIRED"),
    dict(title="ECE Section B: Lab Rescheduled", message="The VLSI Design lab session for Section B has been rescheduled to Friday, 2 PM.",
         audience="SECTION", audience_detail="ECE — Section B", priority="NORMAL",
         published_offset=-1, expiration_offset=3, status="ACTIVE"),
    dict(title="Draft: Annual Sports Meet Announcement", message="Draft announcement for the upcoming annual sports meet — pending final schedule confirmation.",
         audience="ALL_STUDENTS", audience_detail="All Students", priority="NORMAL",
         published_offset=0, expiration_offset=30, status="DRAFT"),
    dict(title="Mechanical Dept: Industrial Visit Consent Forms", message="Students attending the industrial visit must submit signed consent forms by Thursday.",
         audience="DEPARTMENT", audience_detail="Mechanical Engineering", priority="IMPORTANT",
         published_offset=-4, expiration_offset=2, status="ACTIVE"),
]

_AUDIENCE_LABELS = {
    "ALL_STUDENTS": "All Students",
    "DEPARTMENT": "Department",
    "SEMESTER": "Semester",
    "SECTION": "Section",
    "GROUP": "Specific Group",
}

_notifications_cache: list[Notification] | None = None


def _estimate_recipients(audience: str, audience_detail: str) -> int:
    students = get_all_students()
    if audience == "ALL_STUDENTS":
        return len(students)
    if audience == "DEPARTMENT":
        return len([s for s in students if s.department == audience_detail])
    if audience == "SEMESTER":
        try:
            sem = int(audience_detail.split()[-1])
        except (ValueError, IndexError):
            return 0
        return len([s for s in students if s.semester == sem])
    if audience == "SECTION":
        return max(15, len(students) // 15)
    return max(10, len(students) // 20)


def _build_seed() -> list[Notification]:
    result = []
    for i, item in enumerate(_SEED_NOTIFICATIONS, start=1):
        result.append(
            Notification(
                notification_id=f"N{i:03d}",
                title=item["title"],
                message=item["message"],
                audience=item["audience"],
                audience_detail=item["audience_detail"],
                priority=item["priority"],
                published_by="Admin",
                published_date=days_from_today(item["published_offset"]),
                expiration_date=days_from_today(item["expiration_offset"]),
                status=item["status"],
                recipient_count=_estimate_recipients(item["audience"], item["audience_detail"]),
            )
        )
    return result


def get_all_notifications() -> list[Notification]:
    global _notifications_cache
    if _notifications_cache is None:
        _notifications_cache = _build_seed()
    return _notifications_cache


def audience_label(audience_code: str) -> str:
    return _AUDIENCE_LABELS.get(audience_code, audience_code)


def add_notification(title: str, message: str, audience: str, audience_detail: str,
                      priority: str, expiration_date: str, published_by: str = "Admin") -> Notification:
    """Adds a notification to the in-memory mock store and returns it.
    Stage 2 replaces this with POST /api/notifications."""
    notifications = get_all_notifications()
    notification = Notification(
        notification_id=new_id("N"),
        title=title.strip(),
        message=message.strip(),
        audience=audience,
        audience_detail=audience_detail,
        priority=priority,
        published_by=published_by,
        published_date=days_from_today(0),
        expiration_date=expiration_date,
        status="ACTIVE",
        recipient_count=_estimate_recipients(audience, audience_detail),
    )
    notifications.insert(0, notification)
    return notification

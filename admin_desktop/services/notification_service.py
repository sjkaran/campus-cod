"""
Notification service — Stage 2 (live backend).

GET /notifications/admin, POST /notifications. The backend's audience
model has exactly 4 types (ALL_STUDENTS, DEPARTMENT, SEMESTER, SECTION) —
there is no server-side "named group" concept, so that option has been
removed from the composer (Stage 1 mock had an extra placeholder option).

Note: the admin listing endpoint returns audience_type but not the specific
target (e.g. which department) for past notifications, and has no
recipient-count field — those two things are only known at publish time.
"""

from models.notification import Notification
from api.api_client import api_client, ApiClientError
from services import student_service
from utils.helpers import now_str

_AUDIENCE_OPTIONS = [
    ("ALL_STUDENTS", "All Students"),
    ("DEPARTMENT", "Department"),
    ("SEMESTER", "Semester"),
    ("SECTION", "Section"),
]

_AUDIENCE_LABELS = dict(_AUDIENCE_OPTIONS)


def get_audience_options() -> list[tuple[str, str]]:
    return list(_AUDIENCE_OPTIONS)


def get_priority_options() -> list[str]:
    return ["Normal", "Important", "Urgent"]


def audience_label(code: str) -> str:
    return _AUDIENCE_LABELS.get(code, code)


def get_notifications(search: str = "", priority: str = "All", status: str = "All",
                       audience: str = "All") -> list[Notification]:
    """FUTURE (now live): GET /notifications/admin"""
    try:
        rows = api_client.get_all_pages("/notifications/admin", page_size=100)
    except ApiClientError:
        return []

    notifications = []
    for r in rows:
        notifications.append(Notification(
            notification_id=f"N{r['id']:03d}",
            title=r["title"], message=r.get("message", ""),
            audience=r["audience_type"], audience_detail=audience_label(r["audience_type"]),
            priority=r["priority"], published_by=r.get("author_name") or "—",
            published_date=(r.get("created_at") or "")[:10],
            expiration_date=(r.get("expires_at") or "")[:10] if r.get("expires_at") else "",
            status=r.get("status", "ACTIVE"), recipient_count=0,
        ))

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


def _targets_for(audience_code: str, audience_detail: str) -> list[dict]:
    if audience_code == "ALL_STUDENTS":
        return []
    if audience_code == "DEPARTMENT":
        code = student_service.code_for_department_name(audience_detail)
        return [{"department_code": code}] if code else []
    if audience_code == "SEMESTER":
        try:
            return [{"semester": int(audience_detail.split()[-1])}]
        except (ValueError, IndexError):
            return []
    if audience_code == "SECTION":
        section = audience_detail.replace("Section", "").strip()
        return [{"section": section}] if section else []
    return []


def publish_notification(title: str, message: str, audience_code: str, audience_detail: str,
                          priority: str, expiration_date: str, published_by: str = "Admin") -> Notification:
    """FUTURE (now live): POST /notifications"""
    payload = {
        "title": title.strip(),
        "message": message.strip(),
        "priority": priority.upper(),
        "audience_type": audience_code,
        "targets": _targets_for(audience_code, audience_detail),
    }
    if expiration_date:
        payload["expires_at"] = f"{expiration_date}T23:59:59"

    result = api_client.post("/notifications", payload)
    r = result["data"]
    return Notification(
        notification_id=f"N{r['id']:03d}", title=r["title"], message=r.get("message", ""),
        audience=r["audience_type"], audience_detail=audience_detail, priority=r["priority"],
        published_by=r.get("author_name") or published_by,
        published_date=(r.get("created_at") or "")[:10],
        expiration_date=(r.get("expires_at") or "")[:10] if r.get("expires_at") else "",
        status=r.get("status", "ACTIVE"), recipient_count=0,
    )


def estimate_audience_size(audience_code: str, audience_detail: str) -> int:
    """Approximates recipient count from /students, since the backend has
    no dedicated 'audience size' endpoint."""
    try:
        if audience_code == "ALL_STUDENTS":
            resp = api_client.get("/students", params={"page_size": 1})
        elif audience_code == "DEPARTMENT":
            code = student_service.code_for_department_name(audience_detail)
            resp = api_client.get("/students", params={"department": code, "page_size": 1})
        elif audience_code == "SEMESTER":
            sem = int(audience_detail.split()[-1])
            resp = api_client.get("/students", params={"semester": sem, "page_size": 1})
        elif audience_code == "SECTION":
            section = audience_detail.replace("Section", "").strip()
            resp = api_client.get("/students", params={"section": section, "page_size": 1})
        else:
            return 0
        return (resp.get("pagination") or {}).get("total", 0)
    except (ApiClientError, ValueError, IndexError):
        return 0

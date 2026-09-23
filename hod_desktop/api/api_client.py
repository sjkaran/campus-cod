"""
Future REST API client for the Smart Campus backend.

Stage 1: this module is a stub. Nothing in the UI calls it yet — all
data flows through mock/mock_data.py via the services layer.

Stage 2: this becomes the real HTTP client (requests/httpx) that the
services layer switches to once config.settings.DATA_SOURCE_MODE is
set to "api". Every method signature here mirrors a documented
endpoint so that swapping MockService -> ApiService in services/*.py
is a drop-in replacement with no UI changes required.
"""

from config.settings import API_BASE_URL


class ApiClient:
    """
    Thin HTTP wrapper around the future FastAPI backend.

    Each method below corresponds to a documented endpoint (see the
    "Future API" comments in the relevant services/*.py file). None of
    these are implemented yet — calling any of them raises
    NotImplementedError so that accidental Stage-1 usage fails loudly
    instead of silently doing nothing.
    """

    def __init__(self, base_url: str = API_BASE_URL, token: str | None = None):
        self.base_url = base_url
        self.token = token  # JWT, attached as an Authorization header in Stage 2

    # ---- Auth ----------------------------------------------------
    def login(self, hod_id: str, password: str):
        # POST /api/auth/login
        raise NotImplementedError("Stage 2: implement HTTP call to /api/auth/login")

    # ---- Dashboard -------------------------------------------------
    def get_dashboard_summary(self):
        # GET /api/hod/dashboard
        raise NotImplementedError

    # ---- Gate passes ------------------------------------------------
    def get_pending_gatepasses(self):
        # GET /api/gatepasses/pending
        raise NotImplementedError

    def get_gatepass_details(self, request_id: str):
        # GET /api/gatepasses/{id}
        raise NotImplementedError

    def approve_gatepass(self, request_id: str):
        # PATCH /api/gatepasses/{id}/approve
        raise NotImplementedError

    def reject_gatepass(self, request_id: str, reason: str):
        # PATCH /api/gatepasses/{id}/reject
        raise NotImplementedError

    # ---- Notifications -----------------------------------------------
    def publish_notification(self, payload: dict):
        # POST /api/notifications
        raise NotImplementedError

    def get_my_notifications(self):
        # GET /api/notifications/created-by-me
        raise NotImplementedError

    # ---- Attendance --------------------------------------------------
    def get_department_attendance(self, filters: dict):
        # GET /api/attendance/department
        raise NotImplementedError

    def get_student_attendance(self, student_id: str):
        # GET /api/attendance/student/{id}
        raise NotImplementedError

    # ---- Analytics ---------------------------------------------------
    def get_department_analytics(self):
        # GET /api/analytics/department/attendance
        raise NotImplementedError

    def get_subject_analytics(self):
        # GET /api/analytics/department/subjects
        raise NotImplementedError

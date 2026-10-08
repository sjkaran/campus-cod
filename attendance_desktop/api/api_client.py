"""API client boundary. The ONLY module that knows about endpoints / mock storage."""
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import List

from config import settings
from mock import data as mock
from models.models import (
    AcademicGroup, AttendanceRecord, AttendanceReport, AttendanceSession,
    Faculty, Student, Subject, SUBMITTED,
)


class ApiError(Exception): ...


# ---------------------------------------------------------------------------
# Stage 1: in-memory mock client
# ---------------------------------------------------------------------------

class MockApiClient:
    """Stage 1: in-memory stand-in for the central backend."""
    def __init__(self):
        self._reports = {r.session.session_id: r for r in mock.seed_history("FAC001")}
        self._sub_n = 3

    # FUTURE: POST /api/auth/login
    def login(self, username, password) -> Faculty:
        e = mock.FACULTY.get(username)
        if not e or e[0] != password: raise ApiError("Invalid Faculty ID or password.")
        return e[1]

    def get_subjects(self) -> List[Subject]: return mock.SUBJECTS          # GET /api/faculty/subjects
    def get_groups(self) -> List[AcademicGroup]: return mock.GROUPS        # GET /api/faculty/classes
    def get_students(self, g: AcademicGroup): return mock.students_for(g)  # GET /api/faculty/classes/{id}/students

    def list_reports(self) -> List[AttendanceReport]:                      # GET /api/attendance/sessions/my
        return sorted(self._reports.values(), key=lambda r: (r.session.date, r.session.start_time), reverse=True)

    def save_report(self, r: AttendanceReport) -> None:                    # local persistence only (Stage 1)
        self._reports[r.session.session_id] = r

    def submit_report(self, payload: dict) -> dict:                        # POST /api/attendance/sessions/{id}/submit
        if settings.MOCK_SUBMIT_FAILS: raise ApiError("Unable to submit the attendance report.")
        self._sub_n += 1
        return {"success": True, "submission_id": f"ATT-SUB-{self._sub_n:03d}"}


# ---------------------------------------------------------------------------
# Stage 2: live HTTP client
# ---------------------------------------------------------------------------

class HttpApiClient:
    """Stage 2: real HTTP calls against settings.API_BASE_URL using stdlib urllib."""

    def __init__(self):
        self._base_url = settings.API_BASE_URL.rstrip("/")
        self._token: str | None = None
        # Populated after login; used to map external_session_id -> backend int id
        self._session_id_map: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _url(self, path: str, params: dict | None = None) -> str:
        url = self._base_url + path
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url += "?" + urllib.parse.urlencode(clean)
        return url

    def _request(self, method: str, path: str, params: dict = None, body: dict = None) -> dict:
        url = self._url(path, params)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                text = resp.read().decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(raw).get("detail", raw)
            except (json.JSONDecodeError, AttributeError):
                detail = raw or e.reason
            raise ApiError(str(detail)) from e
        except urllib.error.URLError as e:
            raise ApiError(
                f"Cannot reach the backend at {self._base_url}. Is it running? ({e.reason})"
            ) from e

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> Faculty:
        """POST /api/auth/login — validates FACULTY role, stores JWT."""
        resp = self._request("POST", "/api/auth/login", body={"username": username, "password": password})
        user = resp.get("user", {})
        if user.get("role") != "FACULTY":
            raise ApiError("Access denied. This application is for Faculty accounts only.")
        self._token = resp["access_token"]
        # Fetch full profile to get department_code
        profile_resp = self._request("GET", "/api/faculty/me")
        profile = profile_resp.get("data", {})
        return Faculty(
            faculty_id=profile.get("faculty_id", username),
            name=profile.get("name", user.get("name", "")),
            department=profile.get("department_code", user.get("department_code", "")),
        )

    def get_subjects(self) -> List[Subject]:
        """GET /api/faculty/me — extract subjects from assignments."""
        resp = self._request("GET", "/api/faculty/me")
        assignments = resp.get("data", {}).get("assignments", [])
        seen, subjects = set(), []
        for a in assignments:
            s = a.get("subject", {})
            sid = s.get("id")
            if sid not in seen:
                seen.add(sid)
                subjects.append(Subject(
                    subject_id=str(sid),
                    name=s.get("name", ""),
                    code=s.get("code", ""),
                    department_id=str(s.get("department_id", "")),
                ))
        return subjects

    def get_groups(self) -> List[AcademicGroup]:
        """GET /api/faculty/me — extract academic classes from assignments."""
        resp = self._request("GET", "/api/faculty/me")
        assignments = resp.get("data", {}).get("assignments", [])
        seen, groups = set(), []
        for a in assignments:
            c = a.get("academic_class", {})
            cid = c.get("id")
            if cid not in seen:
                seen.add(cid)
                groups.append(AcademicGroup(
                    department_id=c.get("department_code", ""),
                    department=c.get("department_code", ""),
                    semester=c.get("semester", 0),
                    section=c.get("section", ""),
                ))
        return groups

    def get_students(self, group: AcademicGroup) -> List[Student]:
        """GET /api/students?department=X&semester=Y&section=Z — all pages."""
        params = {
            "department": group.department_id,
            "semester": group.semester,
            "section": group.section,
            "page_size": 100,
        }
        students, page = [], 1
        while True:
            params["page"] = page
            resp = self._request("GET", "/api/students", params=params)
            items = resp.get("data") or []
            for item in items:
                students.append(Student(
                    student_id=item.get("student_public_id", str(item.get("id", ""))),
                    name=item.get("name", ""),
                    roll_no=item.get("roll_no", ""),
                ))
            pagination = resp.get("pagination") or {}
            total = pagination.get("total", len(students))
            if not items or len(students) >= total:
                break
            page += 1
        return students

    def list_reports(self) -> List[AttendanceReport]:
        """GET /api/attendance/sessions/my — all pages, mapped to AttendanceReport."""
        params = {"page_size": 100}
        sessions, page = [], 1
        while True:
            params["page"] = page
            resp = self._request("GET", "/api/attendance/sessions/my", params=params)
            items = resp.get("data") or []
            sessions.extend(items)
            pagination = resp.get("pagination") or {}
            total = pagination.get("total", len(sessions))
            if not items or len(sessions) >= total:
                break
            page += 1

        reports = []
        for item in sessions:
            backend_id = item.get("id")
            ext_id = item.get("external_session_id") or str(backend_id)
            # Cache the mapping so submit_report can find the backend integer id
            self._session_id_map[ext_id] = backend_id

            session = AttendanceSession(
                session_id=ext_id,
                faculty_id=item.get("faculty_name", ""),
                department_id="",
                semester=0,
                section=item.get("class_label", ""),
                subject_id=str(item.get("subject_id", "")),
                subject_name=item.get("subject_name", ""),
                date=str(item.get("date", "")),
                start_time=str(item.get("start_time") or ""),
                end_time=str(item.get("end_time") or ""),
                status=item.get("status", SUBMITTED),
                submission_id=item.get("external_session_id"),
            )
            present = item.get("present", 0)
            absent = item.get("absent", 0)
            total_s = present + absent
            pct = round(100 * present / total_s, 1) if total_s else 0.0
            reports.append(AttendanceReport(
                session=session,
                total_students=total_s,
                present=present,
                absent=absent,
                attendance_percentage=pct,
            ))
        return sorted(reports, key=lambda r: (r.session.date, r.session.start_time), reverse=True)

    def save_report(self, report: AttendanceReport) -> None:
        """No-op: backend persists on submit. Local session state is managed by the service layer."""
        pass

    def submit_report(self, payload: dict) -> dict:
        """POST /api/attendance/sessions/{backend_id}/submit."""
        ext_id = payload.get("session_id", "")
        backend_id = self._session_id_map.get(ext_id)
        if backend_id is None:
            # The session was just created locally (not yet persisted); create it first
            backend_id = self._create_session(payload)
            self._session_id_map[ext_id] = backend_id

        records = [
            {"student_id": r["student_id"], "status": r["status"], "marked_at": r.get("marked_at") or None}
            for r in payload.get("attendance", [])
        ]
        resp = self._request(
            "POST",
            f"/api/attendance/sessions/{backend_id}/submit",
            body={"records": records},
        )
        return {
            "success": resp.get("success", True),
            "submission_id": str(resp.get("session_id", backend_id)),
        }

    # ------------------------------------------------------------------
    # Internal: create a session on the backend when submitting a new one
    # ------------------------------------------------------------------

    def _create_session(self, payload: dict) -> int:
        """POST /api/attendance/sessions to persist a new session, returns backend int id."""
        # Resolve subject and class ids from their string identifiers
        subject_id = self._resolve_subject_id(payload.get("subject_id", ""))
        class_id = self._resolve_class_id(
            department=payload.get("department_id", ""),
            semester=payload.get("semester"),
            section=payload.get("section", ""),
        )
        body = {
            "external_session_id": payload.get("session_id"),
            "subject_id": subject_id,
            "academic_class_id": class_id,
            "date": payload.get("date"),
            "start_time": payload.get("start_time") or None,
            "end_time": payload.get("end_time") or None,
        }
        resp = self._request("POST", "/api/attendance/sessions", body=body)
        session_data = resp.get("data", {})
        backend_id = session_data.get("id")
        if not backend_id:
            raise ApiError("Failed to create attendance session on the backend.")
        # Move session to CLOSED so submit is valid
        self._request("PATCH", f"/api/attendance/sessions/{backend_id}/status", body={"status": "CLOSED"})
        return backend_id

    def _resolve_subject_id(self, subject_id_str: str) -> int:
        """Subjects fetched via get_subjects() use str(backend_id) as subject_id."""
        try:
            return int(subject_id_str)
        except (ValueError, TypeError):
            raise ApiError(f"Cannot resolve backend subject id from '{subject_id_str}'.")

    def _resolve_class_id(self, department: str, semester: int, section: str) -> int:
        """GET /api/academic-classes filtered by dept/semester/section, return backend id."""
        resp = self._request("GET", "/api/academic-classes", params={"department": department})
        for c in resp.get("data", []):
            if c.get("semester") == semester and c.get("section") == section:
                return c["id"]
        raise ApiError(f"Cannot find class for {department} sem {semester} section {section}.")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_api_client():
    return MockApiClient() if settings.USE_MOCK_API else HttpApiClient()

"""API client boundary. The ONLY module that knows about endpoints / mock storage."""
from typing import List
from config import settings
from mock import data as mock
from models.models import *

class ApiError(Exception): ...

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

class HttpApiClient(MockApiClient):
    """Stage 2 placeholder: implement each method with httpx against settings.API_BASE_URL + JWT."""
    def __init__(self): raise NotImplementedError("Implement HTTP calls in Stage 2.")

def get_api_client(): return MockApiClient() if settings.USE_MOCK_API else HttpApiClient()

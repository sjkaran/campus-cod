"""
Student service — Stage 2 (live backend).

GET /departments, GET /academic-classes, GET /students, GET /students/{id}
are the backend endpoints behind this module. Status (ACTIVE/INACTIVE) has
no server-side filter, so it's applied client-side after fetching.
"""

from dataclasses import dataclass

from models.student import Student
from models.attendance import AttendanceRecord
from models.gatepass import GatePass
from api.api_client import api_client, ApiClientError
from config.settings import ATTENDANCE_WARNING_THRESHOLD

_departments_cache: list[dict] | None = None
_sections_cache: list[str] | None = None


def _load_departments() -> list[dict]:
    global _departments_cache
    if _departments_cache is None:
        _departments_cache = api_client.get_data("/departments") or []
    return _departments_cache


def get_departments() -> list[str]:
    """Display names for the filter dropdowns, e.g. 'Computer Science & Engineering'."""
    return [d["name"] for d in _load_departments()]


def code_for_department_name(name: str) -> str | None:
    for d in _load_departments():
        if d["name"] == name:
            return d["code"]
    return None


def name_for_department_code(code: str) -> str:
    for d in _load_departments():
        if d["code"] == code:
            return d["name"]
    return code or "—"


def get_sections() -> list[str]:
    global _sections_cache
    if _sections_cache is None:
        try:
            classes = api_client.get_data("/academic-classes") or []
            _sections_cache = sorted({c["section"] for c in classes}) or ["A", "B", "C"]
        except ApiClientError:
            _sections_cache = ["A", "B", "C"]
    return _sections_cache


def _to_student(row: dict) -> Student:
    return Student(
        student_id=row["student_id"],
        name=row["name"],
        roll_number=row.get("roll_number", ""),
        department=name_for_department_code(row.get("department_code")),
        semester=row.get("semester", 0),
        section=row.get("section", ""),
        email=row.get("email", ""),
        status=row.get("status", "ACTIVE"),
        phone=row.get("phone") or "",
        admission_year=0,  # not modeled by the backend yet
        pk=row.get("id", 0),
    )


def get_students(search: str = "", department: str = "All", semester: str = "All",
                  section: str = "All", status: str = "All") -> list[Student]:
    """FUTURE (now live): GET /students?department=&semester=&section=&q="""
    params = {
        "department": code_for_department_name(department) if department != "All" else None,
        "semester": int(semester) if semester != "All" else None,
        "section": section if section != "All" else None,
        "q": search.strip() if search else None,
    }
    try:
        rows = api_client.get_all_pages("/students", params=params)
    except ApiClientError:
        return []

    students = [_to_student(r) for r in rows]
    if status != "All":
        students = [s for s in students if s.status == status]
    return students


def get_student_by_id(student_id: str) -> Student | None:
    """Looks up a student by their PUBLIC id (e.g. S2026001) via search."""
    try:
        rows = api_client.get("/students", params={"q": student_id, "page_size": 5}).get("data", [])
    except ApiClientError:
        return None
    for row in rows:
        if row["student_id"] == student_id:
            return _to_student(row)
    return None


@dataclass
class GatePassSummary:
    total: int
    approved: int
    rejected: int
    pending: int


@dataclass
class StudentDetail:
    student: Student
    overall_attendance: float
    subject_attendance: list  # list[AttendanceRecord]
    attendance_warning: bool
    gatepass_summary: GatePassSummary
    recent_gatepasses: list  # list[GatePass]


def get_student_details(student_id: str) -> StudentDetail | None:
    """Composed from several endpoints, since the backend has no single
    'full student detail' resource:
        GET /students?q=                (find the student + their class)
        GET /reports/attendance?...      (subject-level attendance for their class)
        GET /gatepasses?department=...   (gate-pass history for their department)
    """
    try:
        rows = api_client.get("/students", params={"q": student_id, "page_size": 5}).get("data", [])
    except ApiClientError:
        return None
    raw = next((r for r in rows if r["student_id"] == student_id), None)
    if not raw:
        return None
    student = _to_student(raw)

    # Subject-level attendance for this student's class, filtered down to them.
    try:
        report_rows = api_client.get_all_pages("/reports/attendance", params={
            "department": raw.get("department_code"),
            "semester": raw.get("semester"),
            "section": raw.get("section"),
        })
    except ApiClientError:
        report_rows = []
    my_rows = [r for r in report_rows if r.get("student_id") == student_id]

    total_present = sum(r.get("present", 0) for r in my_rows)
    total_held = sum(r.get("total_classes", 0) for r in my_rows)
    overall = round((total_present / total_held) * 100, 1) if total_held else 0.0

    subject_attendance = [
        AttendanceRecord(
            student_id=student_id, student_name=student.name, department=student.department,
            semester=student.semester, section=student.section,
            subject=r.get("subject_name", r.get("subject_code", "")),
            classes_held=r.get("total_classes", 0), present=r.get("present", 0),
            absent=r.get("absent", 0), date="",
        )
        for r in my_rows
    ]

    # Gate-pass history, filtered down to this student from their department's list.
    try:
        gp_rows = api_client.get_all_pages("/gatepasses", params={"department": raw.get("department_code")})
    except ApiClientError:
        gp_rows = []
    my_gp = [g for g in gp_rows if g.get("student_public_id") == student_id]

    gatepasses = [
        GatePass(
            request_id=f"GP{g['id']:04d}", student_id=student_id, student_name=student.name,
            department=student.department, destination=g.get("destination", ""),
            reason=g.get("reason", ""), departure_date=g.get("departure_date", ""),
            return_date=g.get("return_date", ""), submitted_date=(g.get("created_at") or "")[:10],
            status=g.get("status", ""), reviewing_authority=g.get("hod_name") or "—",
            remarks=g.get("hod_remarks") or "", pk=g["id"],
        )
        for g in my_gp
    ]
    gatepasses.sort(key=lambda g: g.submitted_date, reverse=True)

    gp_summary = GatePassSummary(
        total=len(gatepasses),
        approved=len([g for g in gatepasses if g.status == "APPROVED"]),
        rejected=len([g for g in gatepasses if g.status == "REJECTED"]),
        pending=len([g for g in gatepasses if g.status == "PENDING"]),
    )

    return StudentDetail(
        student=student,
        overall_attendance=overall,
        subject_attendance=subject_attendance,
        attendance_warning=overall < ATTENDANCE_WARNING_THRESHOLD,
        gatepass_summary=gp_summary,
        recent_gatepasses=gatepasses[:5],
    )

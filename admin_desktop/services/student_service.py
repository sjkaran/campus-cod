"""
Student service.

Stage 1: getStudents()/getStudentDetails() -> mock.students
Stage 2: -> ApiClient -> GET /api/students, GET /api/students/{id}
"""

from dataclasses import dataclass

from models.student import Student
from mock.students import get_all_students, DEPARTMENTS, SECTIONS
from mock.attendance import get_attendance_for_student
from mock.gatepasses import get_gatepasses_for_student
from config.settings import ATTENDANCE_WARNING_THRESHOLD


def get_departments() -> list[str]:
    return DEPARTMENTS


def get_sections() -> list[str]:
    return SECTIONS


def get_students(search: str = "", department: str = "All", semester: str = "All",
                  section: str = "All", status: str = "All") -> list[Student]:
    """Returns students matching the given filters.

    FUTURE API INTEGRATION
        GET /api/students?search=&department=&semester=&section=&status=
    """
    students = get_all_students()
    search = (search or "").strip().lower()

    def matches(s: Student) -> bool:
        if department != "All" and s.department != department:
            return False
        if semester != "All" and str(s.semester) != str(semester):
            return False
        if section != "All" and s.section != section:
            return False
        if status != "All" and s.status != status:
            return False
        if search:
            haystack = f"{s.student_id} {s.name} {s.roll_number}".lower()
            if search not in haystack:
                return False
        return True

    return [s for s in students if matches(s)]


def get_student_by_id(student_id: str) -> Student | None:
    for s in get_all_students():
        if s.student_id == student_id:
            return s
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
    subject_attendance: list
    attendance_warning: bool
    gatepass_summary: GatePassSummary
    recent_gatepasses: list


def get_student_details(student_id: str) -> StudentDetail | None:
    """FUTURE API INTEGRATION:
        GET /api/students/{id}
        GET /api/students/{id}/attendance
        GET /api/students/{id}/gatepasses
    """
    student = get_student_by_id(student_id)
    if not student:
        return None

    records = get_attendance_for_student(student_id)
    total_present = sum(r.present for r in records)
    total_held = sum(r.classes_held for r in records)
    overall = round((total_present / total_held) * 100, 1) if total_held else 0.0

    gatepasses = get_gatepasses_for_student(student_id)
    gp_summary = GatePassSummary(
        total=len(gatepasses),
        approved=len([g for g in gatepasses if g.status == "APPROVED"]),
        rejected=len([g for g in gatepasses if g.status == "REJECTED"]),
        pending=len([g for g in gatepasses if g.status == "PENDING"]),
    )
    recent_gatepasses = sorted(gatepasses, key=lambda g: g.submitted_date, reverse=True)[:5]

    return StudentDetail(
        student=student,
        overall_attendance=overall,
        subject_attendance=records,
        attendance_warning=overall < ATTENDANCE_WARNING_THRESHOLD,
        gatepass_summary=gp_summary,
        recent_gatepasses=recent_gatepasses,
    )

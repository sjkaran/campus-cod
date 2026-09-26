"""
Mock gate-pass dataset.

FUTURE API INTEGRATION
Replace this module's data source with:
    GET /api/gatepasses
    GET /api/gatepasses/{id}

NOTE: The Admin node only ever READS gate-pass data here. Approval /
rejection belongs to the HOD node's authorization model, not Admin.
"""

import random

from models.gatepass import GatePass
from mock.students import get_all_students
from utils.helpers import days_from_today

_DESTINATIONS = ["Home", "Hospital", "Local Errand", "Family Function", "Internship", "Exam Center", "Bank Work"]
_REASONS = [
    "Weekend home visit", "Medical appointment", "Family emergency",
    "Attending a wedding", "Internship interview", "Document submission",
    "Personal work", "Sibling's function",
]
_HODS = {
    "Computer Science": "Dr. A. Krishnan (HOD, CSE)",
    "Electronics & Communication": "Dr. S. Bannerjee (HOD, ECE)",
    "Mechanical Engineering": "Dr. R. Iyengar (HOD, ME)",
    "Civil Engineering": "Dr. M. Fernandes (HOD, CE)",
    "Electrical Engineering": "Dr. P. Suresh (HOD, EE)",
}

_STATUS_WEIGHTS = [("PENDING", 0.30), ("APPROVED", 0.55), ("REJECTED", 0.15)]

_GATEPASS_CACHE: list[GatePass] | None = None


def _weighted_status(rng: random.Random) -> str:
    r = rng.random()
    acc = 0.0
    for status, weight in _STATUS_WEIGHTS:
        acc += weight
        if r <= acc:
            return status
    return "PENDING"


def _generate_gatepasses(seed: int = 11) -> list[GatePass]:
    rng = random.Random(seed)
    students = get_all_students()
    sample_pool = rng.sample(students, k=min(160, len(students)))
    records = []
    for i, student in enumerate(sample_pool, start=1):
        status = _weighted_status(rng)
        submitted_offset = -rng.randint(1, 30)
        departure_offset = submitted_offset + rng.randint(1, 5)
        return_offset = departure_offset + rng.randint(1, 4)
        remarks = ""
        if status == "REJECTED":
            remarks = rng.choice([
                "Insufficient attendance to approve leave.",
                "Conflicts with upcoming internal exams.",
                "Documentation incomplete — resubmission required.",
            ])
        elif status == "APPROVED":
            remarks = "Approved as requested."

        records.append(
            GatePass(
                request_id=f"GP{i:04d}",
                student_id=student.student_id,
                student_name=student.name,
                department=student.department,
                destination=rng.choice(_DESTINATIONS),
                reason=rng.choice(_REASONS),
                departure_date=days_from_today(departure_offset),
                return_date=days_from_today(return_offset),
                submitted_date=days_from_today(submitted_offset),
                status=status,
                reviewing_authority=_HODS.get(student.department, "Department HOD"),
                remarks=remarks,
            )
        )
    return records


def get_all_gatepasses() -> list[GatePass]:
    global _GATEPASS_CACHE
    if _GATEPASS_CACHE is None:
        _GATEPASS_CACHE = _generate_gatepasses()
    return _GATEPASS_CACHE


def get_gatepass_by_id(request_id: str) -> GatePass | None:
    for gp in get_all_gatepasses():
        if gp.request_id == request_id:
            return gp
    return None


def get_gatepasses_for_student(student_id: str) -> list[GatePass]:
    return [g for g in get_all_gatepasses() if g.student_id == student_id]

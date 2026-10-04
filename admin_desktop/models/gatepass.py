"""Data model for gate-pass records (Admin has monitoring visibility only)."""

from dataclasses import dataclass


@dataclass
class GatePass:
    request_id: str
    student_id: str
    student_name: str
    department: str
    destination: str
    reason: str
    departure_date: str
    return_date: str
    submitted_date: str
    status: str              # PENDING | APPROVED | REJECTED | CANCELLED
    reviewing_authority: str
    remarks: str = ""
    pk: int = 0  # backend's internal integer id (Stage 2) — not shown in UI

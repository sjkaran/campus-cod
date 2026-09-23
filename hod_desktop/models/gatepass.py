"""Gate-pass request model."""

from dataclasses import dataclass, field
from typing import Optional


class GatePassStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class GatePassRequest:
    request_id: str
    student_id: str
    student_name: str
    department: str
    destination: str
    reason: str
    departure_date: str
    departure_time: str
    expected_return: str
    status: str = GatePassStatus.PENDING
    rejection_reason: Optional[str] = None
    previous_passes_count: int = 0
    previous_pass_note: str = ""
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "GatePassRequest":
        return GatePassRequest(**data)

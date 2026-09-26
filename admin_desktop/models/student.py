"""Data model for a Student record, as seen by the Admin node."""

from dataclasses import dataclass


@dataclass
class Student:
    student_id: str
    name: str
    roll_number: str
    department: str
    semester: int
    section: str
    email: str
    status: str  # "ACTIVE" | "INACTIVE"
    phone: str = ""
    admission_year: int = 0

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

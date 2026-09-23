"""Attendance record model."""

from dataclasses import dataclass


@dataclass
class AttendanceRecord:
    student_id: str
    student_name: str
    department: str
    semester: int
    section: str
    subject: str
    classes_held: int
    present: int

    @property
    def absent(self) -> int:
        return self.classes_held - self.present

    @property
    def percentage(self) -> float:
        if self.classes_held == 0:
            return 0.0
        return round((self.present / self.classes_held) * 100, 1)

    @staticmethod
    def from_dict(data: dict) -> "AttendanceRecord":
        return AttendanceRecord(**data)

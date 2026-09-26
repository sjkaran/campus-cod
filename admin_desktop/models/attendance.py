"""Data models related to attendance monitoring."""

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
    absent: int
    date: str  # most recent session date this aggregate reflects

    @property
    def percentage(self) -> float:
        if self.classes_held == 0:
            return 0.0
        return round((self.present / self.classes_held) * 100, 1)


@dataclass
class AttendanceSummary:
    overall_percentage: float
    department_averages: dict          # {department: pct}
    semester_averages: dict            # {semester: pct}
    students_below_threshold: int
    students_critically_below_threshold: int
    total_students_tracked: int

"""Student model — lightweight dataclass mirroring the future API shape."""

from dataclasses import dataclass


@dataclass
class Student:
    student_id: str
    name: str
    department: str
    semester: int
    section: str

    @staticmethod
    def from_dict(data: dict) -> "Student":
        return Student(
            student_id=data["student_id"],
            name=data["name"],
            department=data["department"],
            semester=data["semester"],
            section=data["section"],
        )

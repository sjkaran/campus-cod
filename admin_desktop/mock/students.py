"""
Mock student dataset.

FUTURE API INTEGRATION
Replace this module's data source with:
    GET /api/students
This module must stay the ONLY place raw student mock data lives — UI and
services never construct Student records by hand.
"""

import random

from models.student import Student

DEPARTMENTS = [
    "Computer Science",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electrical Engineering",
]

DEPARTMENT_CODES = {
    "Computer Science": "CSE",
    "Electronics & Communication": "ECE",
    "Mechanical Engineering": "ME",
    "Civil Engineering": "CE",
    "Electrical Engineering": "EE",
}

SECTIONS = ["A", "B", "C"]

_FIRST_NAMES = [
    "Rahul", "Priya", "Aman", "Sneha", "Vikram", "Anjali", "Karan", "Neha",
    "Rohit", "Pooja", "Arjun", "Divya", "Siddharth", "Kavya", "Aditya",
    "Ishita", "Manish", "Ritu", "Saurabh", "Meera", "Nikhil", "Swati",
    "Varun", "Ananya", "Gaurav", "Tanvi", "Harsh", "Riya", "Yash", "Simran",
    "Abhishek", "Pallavi", "Deepak", "Nisha", "Rajat", "Shreya", "Vivek",
    "Komal", "Ashish", "Preeti",
]
_LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Nair",
    "Iyer", "Mehta", "Joshi", "Chauhan", "Malhotra", "Kapoor", "Bhatt",
    "Rao", "Desai", "Pillai", "Agarwal", "Chopra",
]

_STATUS_WEIGHTS = [("ACTIVE", 0.92), ("INACTIVE", 0.08)]


def _weighted_status(rng: random.Random) -> str:
    r = rng.random()
    acc = 0.0
    for status, weight in _STATUS_WEIGHTS:
        acc += weight
        if r <= acc:
            return status
    return "ACTIVE"


def generate_students(count: int = 240, seed: int = 42) -> list[Student]:
    rng = random.Random(seed)
    students: list[Student] = []
    per_dept_counter = {code: 0 for code in DEPARTMENT_CODES.values()}

    for i in range(1, count + 1):
        department = rng.choice(DEPARTMENTS)
        code = DEPARTMENT_CODES[department]
        per_dept_counter[code] += 1
        semester = rng.randint(1, 8)
        section = rng.choice(SECTIONS)
        admission_year = 2026 - ((semester - 1) // 2) - rng.randint(0, 1)
        first = rng.choice(_FIRST_NAMES)
        last = rng.choice(_LAST_NAMES)
        name = f"{first} {last}"
        roll_seq = per_dept_counter[code]
        roll_number = f"{code}{str(admission_year)[-2:]}{roll_seq:03d}"
        student_id = f"STU{i:04d}"
        email = f"{first.lower()}.{last.lower()}{i}@campus.edu"
        phone = f"9{rng.randint(100000000, 999999999)}"

        students.append(
            Student(
                student_id=student_id,
                name=name,
                roll_number=roll_number,
                department=department,
                semester=semester,
                section=section,
                email=email,
                status=_weighted_status(rng),
                phone=phone,
                admission_year=admission_year,
            )
        )
    return students


# Module-level cache so the "dataset" behaves like a stable table across a
# single application run, the way a real DB-backed API would.
_STUDENTS_CACHE: list[Student] | None = None


def get_all_students() -> list[Student]:
    global _STUDENTS_CACHE
    if _STUDENTS_CACHE is None:
        _STUDENTS_CACHE = generate_students()
    return _STUDENTS_CACHE

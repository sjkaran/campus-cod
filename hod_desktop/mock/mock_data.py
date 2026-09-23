"""
Dedicated mock-data layer.

Every piece of sample data used by the HOD desktop prototype lives here,
in one place, instead of being scattered through UI or service code.
Services import from this module during Stage 1. In Stage 2, services
switch to api/api_client.py instead — this file can then be deleted
without touching UI code.

Data is held in module-level lists so that mutations (approve/reject a
gate pass, publish a notification) persist for the lifetime of the app
session, simulating a backend without needing one.
"""

import itertools
from datetime import datetime, timedelta

_id_counter = itertools.count(1000)


def _next_id(prefix: str) -> str:
    return f"{prefix}-{next(_id_counter)}"


# ------------------------------------------------------------------
# HOD account
# ------------------------------------------------------------------

MOCK_HOD = {
    "hod_id": "HOD001",
    "name": "Dr. Sanjay Mishra",
    "department": "Computer Science & Engineering",
    "designation": "Head of Department",
}

MOCK_CREDENTIALS = {
    "HOD001": "hod123",
}


# ------------------------------------------------------------------
# Students
# ------------------------------------------------------------------

_FIRST_NAMES = [
    "Ananya", "Rohit", "Priya", "Debasish", "Sneha", "Aritra", "Kavya",
    "Manas", "Ishita", "Suman", "Ritika", "Abhinav", "Pooja", "Nikhil",
    "Swati", "Rajesh", "Tanvi", "Bikash", "Meghna", "Saurav", "Divya",
    "Kunal", "Rashmi", "Pritam", "Ankita", "Vikram", "Shreya", "Amit",
]
_LAST_NAMES = [
    "Sahoo", "Nayak", "Das", "Patra", "Mohanty", "Behera", "Panda",
    "Swain", "Rout", "Pradhan", "Jena", "Mishra", "Dash", "Sethi",
]

DEPARTMENT = "Computer Science & Engineering"
SECTIONS = ["A", "B", "C"]
SEMESTERS = [3, 5, 7]
SUBJECTS_BY_SEM = {
    3: ["Data Structures", "Digital Logic", "Discrete Math"],
    5: ["Operating Systems", "Computer Networks", "DBMS"],
    7: ["Machine Learning", "Distributed Systems", "Cloud Computing"],
}


def _generate_students(n=90):
    students = []
    names = list(itertools.product(_FIRST_NAMES, _LAST_NAMES))
    for i in range(n):
        first, last = names[i % len(names)]
        sem = SEMESTERS[i % len(SEMESTERS)]
        section = SECTIONS[i % len(SECTIONS)]
        students.append({
            "student_id": f"CSE{2200 + i}",
            "name": f"{first} {last}",
            "department": DEPARTMENT,
            "semester": sem,
            "section": section,
        })
    return students


MOCK_STUDENTS = _generate_students()
_STUDENT_BY_ID = {s["student_id"]: s for s in MOCK_STUDENTS}


# ------------------------------------------------------------------
# Gate passes
# ------------------------------------------------------------------

_DESTINATIONS = [
    "Home town visit", "City Hospital", "Railway Station", "Bank (KYC update)",
    "Family emergency", "Job interview", "District court", "Passport office",
    "Local market", "Bus stand",
]
_REASONS = [
    "Medical appointment", "Family function", "Personal work", "Health checkup",
    "Document submission", "Interview", "Emergency at home", "Festival leave",
]


def _generate_gatepasses(n=26):
    passes = []
    now = datetime.now()
    for i in range(n):
        student = MOCK_STUDENTS[(i * 3) % len(MOCK_STUDENTS)]
        dep_date = now + timedelta(days=(i % 5) - 1)
        status = [
            "PENDING", "PENDING", "PENDING", "PENDING", "PENDING",
            "APPROVED", "APPROVED", "REJECTED",
        ][i % 8]
        entry = {
            "request_id": _next_id("GP"),
            "student_id": student["student_id"],
            "student_name": student["name"],
            "department": student["department"],
            "destination": _DESTINATIONS[i % len(_DESTINATIONS)],
            "reason": _REASONS[i % len(_REASONS)],
            "departure_date": dep_date.strftime("%Y-%m-%d"),
            "departure_time": f"{9 + (i % 8):02d}:00",
            "expected_return": f"{17 + (i % 5):02d}:00",
            "status": status,
            "rejection_reason": "Insufficient prior notice for outstation travel."
            if status == "REJECTED" else None,
            "previous_passes_count": i % 4,
            "previous_pass_note": (
                f"{i % 4} earlier pass(es) this semester, all returned on time."
                if i % 4 else "No prior gate-pass history this semester."
            ),
            "decided_by": MOCK_HOD["name"] if status != "PENDING" else None,
            "decided_at": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            if status != "PENDING" else None,
        }
        passes.append(entry)
    return passes


MOCK_GATEPASSES = _generate_gatepasses()


# ------------------------------------------------------------------
# Notifications
# ------------------------------------------------------------------

def _generate_notifications():
    now = datetime.now()
    base = [
        {
            "title": "Mid-Semester Exam Schedule Released",
            "message": "The mid-semester examination timetable for CSE has been "
                       "published. Please check the department notice board.",
            "audience": "Department",
            "priority": "High",
            "days_ago": 2,
            "expires_in": 10,
        },
        {
            "title": "Guest Lecture on Cloud Architecture",
            "message": "A guest lecture on modern cloud architecture will be held "
                       "in Seminar Hall 2 on Friday at 2 PM.",
            "audience": "Specific group",
            "priority": "Normal",
            "days_ago": 5,
            "expires_in": 3,
        },
        {
            "title": "Attendance Shortage Warning",
            "message": "Students below 75% attendance must meet their mentors "
                       "before the end of this week.",
            "audience": "Department",
            "priority": "High",
            "days_ago": 7,
            "expires_in": -1,
        },
    ]
    notifications = []
    for item in base:
        created = now - timedelta(days=item["days_ago"])
        expires = created + timedelta(days=item["days_ago"] + item["expires_in"])
        notifications.append({
            "notification_id": _next_id("NT"),
            "title": item["title"],
            "message": item["message"],
            "audience": item["audience"],
            "priority": item["priority"],
            "expiration_date": expires.strftime("%Y-%m-%d"),
            "created_at": created.strftime("%Y-%m-%d %H:%M"),
            "status": "EXPIRED" if expires < now else "PUBLISHED",
        })
    return notifications


MOCK_NOTIFICATIONS = _generate_notifications()


# ------------------------------------------------------------------
# Attendance
# ------------------------------------------------------------------

def _generate_attendance():
    records = []
    seed = 17
    for student in MOCK_STUDENTS:
        sem = student["semester"]
        for subject in SUBJECTS_BY_SEM[sem]:
            seed = (seed * 7 + 13) % 41
            classes_held = 40 + (seed % 10)
            variability = (hash(student["student_id"] + subject) % 45)
            present = max(0, classes_held - variability)
            present = min(present, classes_held)
            records.append({
                "student_id": student["student_id"],
                "student_name": student["name"],
                "department": student["department"],
                "semester": sem,
                "section": student["section"],
                "subject": subject,
                "classes_held": classes_held,
                "present": present,
            })
    return records


MOCK_ATTENDANCE = _generate_attendance()


# ------------------------------------------------------------------
# Mutating helpers (simulate persistence within the session)
# ------------------------------------------------------------------

def approve_gatepass_record(request_id: str, decided_by: str):
    for gp in MOCK_GATEPASSES:
        if gp["request_id"] == request_id:
            gp["status"] = "APPROVED"
            gp["rejection_reason"] = None
            gp["decided_by"] = decided_by
            gp["decided_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            return gp
    raise ValueError(f"Gate pass {request_id} not found")


def reject_gatepass_record(request_id: str, reason: str, decided_by: str):
    for gp in MOCK_GATEPASSES:
        if gp["request_id"] == request_id:
            gp["status"] = "REJECTED"
            gp["rejection_reason"] = reason
            gp["decided_by"] = decided_by
            gp["decided_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            return gp
    raise ValueError(f"Gate pass {request_id} not found")


def add_notification_record(title, message, audience, priority, expiration_date):
    entry = {
        "notification_id": _next_id("NT"),
        "title": title,
        "message": message,
        "audience": audience,
        "priority": priority,
        "expiration_date": expiration_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "PUBLISHED",
    }
    MOCK_NOTIFICATIONS.insert(0, entry)
    return entry

# SMART CAMPUS MANAGEMENT SYSTEM

# ATTENDANCE FACULTY DESKTOP APPLICATION

# NODE DEVELOPMENT PROMPT

Use the previously provided "Smart Campus Management System — Master Development Prompt" as the global architecture and engineering specification.

You are now responsible ONLY for developing the Attendance Faculty Desktop Application.

This node is different from the other Smart Campus nodes because an existing QR-based Smart Attendance System already exists and must be used as the primary functional and UI reference.

Existing project:

GitHub repository:

https://github.com/Deepak-Sahoo7/smart-Qr-attendance-system

Relevant directory:

deskapk/

The existing project is the source/reference for the QR attendance functionality.

==================================================

1. CRITICAL INSTRUCTION — INSPECT THE EXISTING PROJECT FIRST
   ==================================================

Before writing any code:

1. Inspect the provided GitHub repository.
2. Inspect the complete `deskapk/` directory.
3. Understand its:

   * folder structure
   * source files
   * UI screens
   * navigation
   * QR generation/scanning workflow
   * attendance workflow
   * session management
   * report generation
   * local data handling
   * dependencies
   * existing business logic
   * existing data models
4. Identify which functionality can be reused.
5. Identify which functionality should be adapted.
6. Identify which functionality should NOT be carried into the Smart Campus system.
7. Preserve useful existing functionality rather than recreating equivalent functionality from scratch.

Do not assume the existing project structure.

Do not rewrite working QR-attendance functionality merely to make the architecture look different.

The existing project is the functional reference.

==================================================
2. OBJECTIVE
============

Build the Attendance Faculty Node of the Smart Campus Management System by adapting the existing QR attendance application into a campus-system-integrated faculty desktop application.

The resulting application should combine:

EXISTING QR ATTENDANCE FUNCTIONALITY

*

SMART CAMPUS FACULTY WORKFLOW

*

FUTURE CENTRAL API INTEGRATION

The final node should allow faculty to conduct attendance using the existing QR workflow and eventually submit the resulting attendance data to the central Smart Campus backend.

==================================================
3. ROLE
=======

The user of this application is:

Attendance Faculty.

The faculty member is responsible for conducting attendance sessions.

The faculty can:

* Log in
* View dashboard
* Select/create attendance session
* Select department/class
* Select semester/section
* Select subject
* Start attendance session
* Display/generate the QR code according to the existing system
* Allow students to scan the QR code
* Observe live attendance
* View present/absent information
* Validate attendance
* Close attendance session
* Review attendance report
* Export/download attendance report if supported
* Submit finalized attendance to the Smart Campus platform
* View previous attendance sessions
* Log out

The faculty should NOT have:

* HOD gate-pass approval functionality
* Administrative student-management functionality
* System-wide administrative analytics
* Notification-management functionality intended for Admin/HOD
* Direct database access

==================================================
4. EXISTING QR SYSTEM IS THE FUNCTIONAL AUTHORITY
=================================================

The existing QR attendance system should be treated as the source of truth for the actual QR attendance mechanism during this node-development phase.

Do NOT invent a new QR protocol unless the existing implementation cannot support the required workflow.

Do NOT unnecessarily change:

* QR generation logic
* QR scanning logic
* Session identification
* Attendance marking mechanism
* Existing anti-duplicate mechanism
* Existing report logic

unless there is a clear integration requirement.

First understand how the existing application works.

Then adapt it.

==================================================
5. IMPORTANT ARCHITECTURAL CHANGE
=================================

The existing QR attendance project may have its own data-storage or backend mechanism.

For the Smart Campus system, the eventual architecture is:

```
                ATTENDANCE FACULTY NODE
                          |
                          |
                          ▼
                   Attendance Service
                          |
                          ▼
                     API Client
                          |
                          ▼
                     FastAPI Backend
                          |
                          ▼
                     PostgreSQL
                          |
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
      Student           Admin             HOD
      Website          Desktop           Desktop
```

```

Therefore:

The QR attendance mechanism may remain local to the attendance application during Stage 1.

However, finalized attendance records must eventually be sent to the central Smart Campus backend.

==================================================
6. STAGE 1 — NODE DEVELOPMENT
==================================================

During the current phase:

DO NOT implement:

- Central PostgreSQL database
- Central FastAPI backend
- Real Smart Campus authentication
- Real Smart Campus REST API
- Production deployment

Instead:

- Reuse/adapt the existing QR attendance functionality.
- Use mock campus data where required.
- Create a clean service/API boundary.
- Allow attendance records to be generated and finalized locally.
- Simulate submission to the central Smart Campus platform.

The application must be usable without the central backend.

==================================================
7. TARGET ARCHITECTURE
==================================================

Use the following conceptual architecture:

┌──────────────────────────────────────────────┐
│          ATTENDANCE FACULTY DESKTOP          │
│                                              │
│  UI                                          │
│   │                                          │
│   ├── Dashboard                              │
│   ├── Session Management                     │
│   ├── QR Attendance                          │
│   ├── Live Attendance                        │
│   ├── Reports                                │
│   └── History                                │
│                                              │
│               ↓                              │
│          Service Layer                       │
│               ↓                              │
│      Attendance / Session Service            │
│               ↓                              │
│          API Client                          │
│               ↓                              │
│       [MOCK API FOR STAGE 1]                 │
└──────────────────────────────────────────────┘

Later:

API Client
    ↓
FastAPI
    ↓
PostgreSQL
```

The QR subsystem should be treated as an internal capability of the Attendance Faculty Node.

==================================================
8. TECHNOLOGY
=============

Primary technology:

* Python
* Tkinter
* ttk

Reuse existing project dependencies where appropriate.

Do not replace a working dependency without a technical reason.

If the existing project uses additional libraries for:

* QR generation
* QR scanning
* image processing
* report generation
* data handling

evaluate whether those dependencies should be retained.

Document the decision.

==================================================
9. APPLICATION STRUCTURE
========================

Create a professional desktop application.

Recommended conceptual layout:

┌───────────────────────────────────────────────────────────────┐
│ Smart Campus — Attendance Faculty          Faculty: [Name]   │
├────────────────┬──────────────────────────────────────────────┤
│                │                                              │
│ Dashboard      │                                              │
│                │                                              │
│ New Session    │                                              │
│                │              MAIN CONTENT                    │
│ Live Attendance│                                              │
│                │                                              │
│ Reports        │                                              │
│                │                                              │
│ History        │                                              │
│                │                                              │
│ Settings       │                                              │
│                │                                              │
│ Logout         │                                              │
└────────────────┴──────────────────────────────────────────────┘

Adapt this layout to the existing project's UI if its existing design is stronger.

Do not discard a useful existing interface merely for consistency with the other nodes.

==================================================
10. LOGIN
=========

Create a Faculty login screen.

Fields:

* Faculty ID / Username
* Password

Controls:

* Login
* Show/hide password

Stage 1:

Use mock authentication.

Future:

POST /api/auth/login

The backend will eventually determine whether the user has the FACULTY role.

==================================================
11. FACULTY DASHBOARD
=====================

Create a faculty dashboard.

Display:

* Faculty name
* Today's date
* Current/active session
* Today's attendance sessions
* Total sessions conducted
* Recent attendance reports
* Quick action to start a session

Possible KPI cards:

Today's Sessions
Active Session
Students Present
Attendance Submitted

Example:

┌─────────────────┐ ┌─────────────────┐
│ Today's Sessions│ │ Active Session  │
│       4         │ │       AI        │
└─────────────────┘ └─────────────────┘

┌─────────────────┐ ┌─────────────────┐
│ Present         │ │ Submitted       │
│       42        │ │       3         │
└─────────────────┘ └─────────────────┘

==================================================
12. CREATE ATTENDANCE SESSION
=============================

This is the entry point to the existing QR attendance system.

Before starting a session, faculty should specify:

* Department
* Semester
* Section
* Subject
* Date
* Start time
* Duration/session window

Example:

Department: Computer Science
Semester: 6
Section: A
Subject: Artificial Intelligence
Date: 27 September 2026
Start: 09:00
Duration: 50 minutes

Validate the required fields.

Do not allow a session to start without the required academic information.

==================================================
13. QR ATTENDANCE SESSION
=========================

Once a session starts:

Display the QR code using the existing project's QR functionality.

The interface should show:

* Subject
* Department
* Semester
* Section
* Session ID
* Start time
* Remaining session time
* QR code
* Attendance count

Example:

┌──────────────────────────────────────────────────┐
│ Artificial Intelligence                          │
│ CSE — Semester 6 — Section A                    │
│                                                  │
│              ┌──────────────┐                    │
│              │              │                    │
│              │   QR CODE    │                    │
│              │              │                    │
│              └──────────────┘                    │
│                                                  │
│ Session: AI-2026-0927-001                        │
│ Time Remaining: 08:42                            │
│ Students Present: 31                             │
└──────────────────────────────────────────────────┘

Reuse the existing project's QR generation/session mechanism.

Do not create a second unrelated QR system.

==================================================
14. LIVE ATTENDANCE
===================

Display attendance as students are marked.

Show:

* Student ID
* Student name
* Roll number
* Time marked
* Status

Example:

┌─────────┬────────────────┬──────────────┬──────────┐
│ ID      │ Student        │ Time         │ Status   │
├─────────┼────────────────┼──────────────┼──────────┤
│ ST001   │ Rahul Sharma   │ 09:03:21     │ Present  │
│ ST002   │ Priya Singh    │ 09:04:02     │ Present  │
│ ST003   │ Aman Kumar     │ 09:05:17     │ Present  │
└─────────┴────────────────┴──────────────┴──────────┘

Display summary:

Present: 31
Absent: 12
Total: 43

The existing QR system's attendance capture mechanism should be reused.

==================================================
15. DUPLICATE ATTENDANCE
========================

Preserve the existing project's duplicate-attendance protection.

If the existing project contains session/device locking or equivalent mechanisms, inspect and preserve that behavior where compatible.

Do not weaken duplicate prevention.

The UI should clearly communicate duplicate attempts.

Example:

"Attendance already recorded for this session."

The backend will eventually provide authoritative duplicate protection.

Client-side duplicate protection alone must NOT be considered sufficient security.

==================================================
16. ATTENDANCE VALIDATION
=========================

Before final submission, provide a validation/review stage.

Faculty should be able to review:

* Total enrolled students
* Present students
* Absent students
* Attendance percentage
* Duplicate/rejected scans if tracked
* Session details

Provide a clear distinction between:

DRAFT / ACTIVE

and:

FINALIZED

Do not allow accidental finalization.

Before final submission:

"Finalize attendance for this session?"

Buttons:

Cancel
Finalize

==================================================
17. CLOSE SESSION
=================

Provide a controlled session-closing workflow.

When faculty closes the session:

1. Stop accepting new attendance.
2. Finalize the attendance list.
3. Calculate summary.
4. Generate the final attendance record.
5. Mark the session as ready for submission.

Example:

Session Status:

ACTIVE
↓
CLOSED
↓
READY FOR SUBMISSION
↓
SUBMITTED

Do not automatically submit to the future central API during Stage 1.

==================================================
18. ATTENDANCE REPORT
=====================

After a session is closed, provide a report.

Report should contain:

Session information:

* Session ID
* Faculty
* Department
* Semester
* Section
* Subject
* Date
* Start time
* End time

Attendance summary:

* Total students
* Present
* Absent
* Attendance percentage

Student table:

* Student ID
* Name
* Roll number
* Status
* Time marked

Reuse the existing project's report generation if it already provides this capability.

If the existing project supports PDF/CSV/export functionality, preserve it where appropriate.

==================================================
19. SUBMIT TO SMART CAMPUS
==========================

This is the most important new feature introduced by the Smart Campus integration.

After the faculty finalizes attendance:

Provide:

SUBMIT TO SMART CAMPUS

button.

Stage 1 behavior:

The operation should simulate an API submission.

Example:

submitAttendanceReport(report)

The mock service should return:

{
"success": true,
"submission_id": "ATT-SUB-001"
}

Display:

"Attendance submitted successfully."

Future:

POST /api/attendance/sessions/{session_id}/submit

The attendance report sent to the backend should conceptually contain:

{
"session_id": "...",
"faculty_id": "...",
"department_id": "...",
"subject_id": "...",
"semester": 6,
"section": "A",
"date": "...",
"attendance": [
{
"student_id": "...",
"status": "PRESENT",
"marked_at": "..."
}
]
}

The exact API schema will be finalized during backend development.

Do not tightly couple the UI to this provisional schema.

==================================================
20. SUBMISSION STATUS
=====================

Display the state of the attendance report.

Possible states:

DRAFT
ACTIVE
CLOSED
READY_FOR_SUBMISSION
SUBMITTED
SUBMISSION_FAILED

For Stage 1, simulate these states.

This will make the future API integration much easier.

==================================================
21. ATTENDANCE HISTORY
======================

Create a History screen.

Display previously conducted sessions.

Columns:

* Session ID
* Date
* Subject
* Department
* Semester
* Section
* Present
* Absent
* Status
* Submission Status

Provide:

* Search
* Date filter
* Subject filter
* Department filter
* Status filter

Allow faculty to open an individual session report.

Future API:

GET /api/attendance/sessions/my

GET /api/attendance/sessions/{id}

==================================================
22. REPORTS
===========

Create a Reports section.

Allow faculty to view:

* Daily attendance reports
* Subject reports
* Session reports
* Student attendance summaries

Where appropriate, provide:

* Preview
* Export PDF
* Export CSV

Reuse existing report functionality where available.

Do not unnecessarily recreate an existing reporting implementation.

==================================================
23. EXISTING PROJECT REUSE STRATEGY
===================================

After inspecting the `deskapk/` project, classify its components into:

### KEEP

Functionality that can be directly reused.

Examples:

* QR generation
* QR scanning
* Session management
* Attendance capture
* Duplicate prevention
* Report generation

### ADAPT

Functionality that needs modification to fit Smart Campus.

Examples:

* Student identity format
* Faculty identity
* Subject/course structure
* Session metadata
* Attendance storage
* Report format
* Authentication

### REMOVE / DO NOT CARRY FORWARD

Functionality that conflicts with the Smart Campus architecture.

Examples:

* Direct database access from UI
* Hard-coded credentials
* Independent campus-wide user management
* Functionality belonging to Admin/HOD
* Redundant notification systems
* Unnecessary external services

### NEW

Functionality required specifically for Smart Campus.

Examples:

* Smart Campus login
* Academic metadata
* Central API submission
* Submission status
* Smart Campus session identity
* Integration-ready service layer

Document this classification after inspecting the repository.

==================================================
24. DATA MODEL
==============

Define internal models for:

Faculty:

* faculty_id
* name
* department

AttendanceSession:

* session_id
* faculty_id
* department_id
* semester
* section
* subject_id
* date
* start_time
* end_time
* status

AttendanceRecord:

* student_id
* session_id
* status
* marked_at

AttendanceReport:

* session
* total_students
* present
* absent
* attendance_percentage
* records

Do not assume this is the final database schema.

These are client-side/domain models for the node.

==================================================
25. SERVICE LAYER
=================

Create services such as:

authenticateFaculty()

getFacultyProfile()

getSubjects()

getAcademicGroups()

createAttendanceSession()

startQrSession()

getLiveAttendance()

closeAttendanceSession()

getAttendanceReport()

submitAttendanceReport()

getAttendanceHistory()

exportAttendanceReport()

Stage 1:

UI
↓
Service
↓
Existing QR subsystem / mock data

Future:

UI
↓
Service
↓
API Client
↓
FastAPI
↓
PostgreSQL

==================================================
26. API CLIENT BOUNDARY
=======================

Create a centralized API client.

Do not scatter API endpoints throughout the application.

Future API operations may include:

POST /api/auth/login

GET /api/faculty/me

GET /api/faculty/subjects

GET /api/faculty/classes

POST /api/attendance/sessions

GET /api/attendance/sessions/{id}

POST /api/attendance/sessions/{id}/submit

GET /api/attendance/sessions/my

GET /api/attendance/reports/{id}

The exact API contract will be defined later.

The current node must not depend on a running FastAPI server.

==================================================
27. QR SYSTEM / SMART CAMPUS DATA BOUNDARY
==========================================

This distinction is extremely important.

The existing QR attendance mechanism answers:

"Was this student's attendance successfully captured during this attendance session?"

The Smart Campus backend answers:

"How does this finalized attendance record become part of the institution's central attendance system?"

Therefore:

QR mechanism
↓
Local attendance session
↓
Validated attendance report
↓
Smart Campus API
↓
Central database

Do not mix these responsibilities unnecessarily.

==================================================
28. MOCK DATA
=============

Create realistic mock data for:

* Faculty
* Departments
* Subjects
* Classes
* Students
* Attendance sessions
* Attendance records
* Reports

The mock students should correspond to realistic student IDs.

Example:

ST-CSE-001
ST-CSE-002
ST-CSE-003

Use realistic names and academic structures.

Mock data should be isolated from UI code.

==================================================
29. ERROR HANDLING
==================

Handle:

* Invalid login
* Invalid session configuration
* QR initialization failure
* Camera/device failure if applicable
* Duplicate attendance
* Invalid QR
* Expired session
* Session closure
* Report generation failure
* Mock API submission failure

Display useful human-readable messages.

Do not expose raw Python exceptions to users.

==================================================
30. LOADING / EMPTY STATES
==========================

The application should support:

Loading
Success
Empty
Error

Examples:

"Loading attendance..."

"No attendance records have been captured."

"Unable to submit the attendance report."

"QR session expired."

==================================================
31. PROJECT STRUCTURE
=====================

After inspecting the existing `deskapk/` project, preserve useful existing modules where practical.

Create or adapt toward a structure similar to:

attendance_desktop/
│
├── main.py
│
├── config/
│   └── settings.py
│
├── models/
│   ├── faculty.py
│   ├── student.py
│   ├── subject.py
│   ├── session.py
│   ├── attendance.py
│   └── report.py
│
├── services/
│   ├── auth_service.py
│   ├── session_service.py
│   ├── attendance_service.py
│   ├── report_service.py
│   └── submission_service.py
│
├── api/
│   └── api_client.py
│
├── qr/
│   ├── generator.py
│   ├── scanner.py
│   └── session_manager.py
│
├── mock/
│   ├── students.py
│   ├── subjects.py
│   ├── sessions.py
│   └── attendance.py
│
├── ui/
│   ├── login.py
│   ├── dashboard.py
│   ├── session.py
│   ├── live_attendance.py
│   ├── report.py
│   └── history.py
│
└── utils/
├── validators.py
├── formatters.py
└── helpers.py

IMPORTANT:

Do not blindly restructure the existing project.

First inspect it.

If its existing architecture is already suitable, preserve it and introduce the Smart Campus integration layer around it.

==================================================
32. SECURITY
============

The existing QR system may contain security mechanisms.

Inspect them carefully.

Preserve appropriate mechanisms such as:

* Session-specific QR
* Expiration
* Duplicate prevention
* Device/session locking
* Input validation

However, understand that client-side controls are not authoritative security.

The eventual backend must independently validate:

* Faculty identity
* Session identity
* Student identity
* QR/session validity
* Duplicate attendance
* Attendance ownership
* Submission authorization

Do not store backend secrets in the desktop client.

==================================================
33. ROLE SEPARATION
===================

This application belongs exclusively to:

FACULTY

It should not implement:

STUDENT functionality
ADMIN functionality
HOD functionality

The faculty node conducts and submits attendance.

The Admin and HOD nodes consume attendance information later through the central backend.

The Student node consumes personal attendance information.

Architecture:

Faculty
│
│ submit
▼
Central Backend
│
├────► Student
│
├────► Admin
│
└────► HOD

==================================================
34. IMPORTANT INTEGRATION RULE
==============================

Do not make the existing QR project communicate directly with the final Smart Campus database.

The correct eventual architecture is:

Existing QR subsystem
↓
Attendance Faculty Node
↓
Smart Campus API
↓
FastAPI
↓
PostgreSQL

This keeps the QR attendance mechanism modular and prevents the existing attendance application from becoming tightly coupled to the campus database.

==================================================
35. ACCEPTANCE CRITERIA
=======================

The Attendance Faculty Node is complete for Stage 1 when:

1. The existing QR attendance project has been inspected.
2. Existing useful QR functionality has been identified.
3. Existing useful QR functionality has been reused or adapted.
4. Faculty login works with mock credentials.
5. Faculty dashboard works.
6. Faculty can create/configure an attendance session.
7. QR attendance functionality works using the existing implementation.
8. Students can be represented as attendance records.
9. Live attendance can be viewed.
10. Duplicate attendance is handled according to the existing mechanism.
11. Session expiration/closure works.
12. Attendance can be reviewed before finalization.
13. Attendance can be finalized.
14. Attendance reports can be viewed.
15. Existing report-generation functionality is reused where appropriate.
16. Attendance history can be viewed.
17. A "Submit to Smart Campus" workflow exists.
18. Smart Campus submission is mocked in Stage 1.
19. Submission status is represented.
20. API integration boundaries are clearly isolated.
21. No central database is accessed.
22. No FastAPI backend is implemented.
23. No Admin/HOD functionality is added.
24. The application remains usable without the central backend.
25. The existing QR functionality is not unnecessarily rewritten.
26. Mock data is isolated from UI code.
27. The application is modular.
28. The node is ready for future FastAPI integration.

==================================================
36. REQUIRED FINAL REPORT FROM THE CODING AI
============================================

After implementation, provide a technical report containing:

### A. Existing project analysis

Explain:

* Existing project structure
* Important `deskapk/` modules
* QR workflow
* Session workflow
* Attendance workflow
* Existing data flow
* Existing report generation
* Existing security/duplicate-prevention mechanisms

### B. Reuse analysis

Create a table:

| Existing Component | Action     | Reason      |
| ------------------ | ---------- | ----------- |
| QR Generator       | KEEP/ADAPT | ...         |
| Session Manager    | KEEP/ADAPT | ...         |
| Attendance Logic   | KEEP/ADAPT | ...         |
| Reports            | KEEP/ADAPT | ...         |
| Database Layer     | REPLACE    | Central API |
| ...                | ...        | ...         |

### C. New Smart Campus components

Explain what was added specifically for the campus system.

### D. Project structure

Explain every major module.

### E. API boundary

List every future API operation.

### F. Data flow

Explain:

QR
↓
Attendance session
↓
Attendance records
↓
Report
↓
Smart Campus API
↓
Central backend
↓
Database

### G. Running instructions

Explain:

* Dependencies
* Installation
* Starting the application
* Mock credentials
* How to test a sample attendance session

### H. Future integration

Explain exactly which functions currently use mock/local behavior and where they should later be replaced by real API calls.

==================================================
37. FINAL PRINCIPLE
===================

This node is NOT a new attendance system.

It is the Smart Campus integration node built around an already-existing QR attendance system.

Therefore:

DO NOT reinvent the QR mechanism.

DO NOT throw away working functionality.

DO NOT blindly copy the old project's architecture either.

Instead:

INSPECT
↓
UNDERSTAND
↓
REUSE
↓
ADAPT
↓
ISOLATE
↓
INTEGRATE

The existing QR system handles the actual attendance-capture mechanism.

The Smart Campus architecture handles:

* Faculty identity
* Academic context
* Attendance session metadata
* Central submission
* Central storage
* Cross-system availability
* Integration with Student/Admin/HOD nodes

The final result should be a polished Faculty Attendance Desktop Application that feels like a native part of the Smart Campus Management System while preserving the proven QR attendance functionality of the existing project.

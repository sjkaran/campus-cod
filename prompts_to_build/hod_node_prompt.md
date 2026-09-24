# HOD DESKTOP APPLICATION
## Node Development Specification

Use the previously provided Smart Campus Management System Master Development Prompt as the system-wide architectural specification.

You are now responsible ONLY for developing the HOD Desktop Application.

Technology:

- Python
- Tkinter
- ttk
- Modular Python architecture

Do NOT implement the central backend or database.

Use mock data and a service/API abstraction layer for the current development stage.

==================================================
## HOD ROLE
==================================================

The HOD is a departmental authority within the Smart Campus Management System.

The HOD can:

- View dashboard information
- View pending gate-pass requests
- Review individual gate-pass requests
- Approve gate-pass requests
- Reject gate-pass requests
- Provide rejection remarks
- Publish notifications
- View student attendance
- View departmental attendance analytics
- View relevant reports
- Manage their session/logout

The HOD must NOT have unrestricted administrator functionality.

The interface should clearly communicate that this is an HOD-level application.

==================================================
## APPLICATION STRUCTURE
==================================================

Create a professional desktop application with a layout similar to:

┌───────────────────────────────────────────────────────────┐
│ Smart Campus                              HOD: [Name]     │
├───────────────┬───────────────────────────────────────────┤
│               │                                           │
│ Dashboard     │                                           │
│               │                                           │
│ Gate Pass     │             MAIN CONTENT                  │
│               │                                           │
│ Notifications │                                           │
│               │                                           │
│ Attendance    │                                           │
│               │                                           │
│ Analytics     │                                           │
│               │                                           │
│ Reports       │                                           │
│               │                                           │
│ Settings      │                                           │
│               │                                           │
│ Logout        │                                           │
│               │                                           │
└───────────────┴───────────────────────────────────────────┘

Use a consistent navigation sidebar and content area.

==================================================
## SCREEN 1 — LOGIN
==================================================

Create an HOD login screen.

Fields:

- HOD ID / Username
- Password

Controls:

- Login
- Show/hide password if appropriate

For Stage 1, authentication may use mock credentials.

Do NOT implement real authentication.

However, isolate authentication behind a service interface so it can later call:

POST /api/auth/login

After successful login, open the HOD dashboard.

==================================================
## SCREEN 2 — DASHBOARD
==================================================

Create an HOD dashboard containing useful high-level information.

Display cards such as:

- Pending Gate Passes
- Today's Gate Passes
- Department Attendance
- Students Below Attendance Threshold
- Recent Notifications

Example:

┌─────────────────┐ ┌─────────────────┐
│ Pending Passes  │ │ Dept Attendance │
│       12        │ │      84.6%      │
└─────────────────┘ └─────────────────┘

┌─────────────────┐ ┌─────────────────┐
│ Today's Passes  │ │ Low Attendance  │
│        7        │ │       24        │
└─────────────────┘ └─────────────────┘

Include a recent activity section.

Use mock data.

Future API examples:

GET /api/hod/dashboard
GET /api/gatepasses/pending
GET /api/attendance/department/summary

==================================================
## SCREEN 3 — GATE PASS MANAGEMENT
==================================================

This is the most important HOD feature.

Create a gate-pass management interface.

Display pending requests in a table.

Columns:

- Request ID
- Student ID
- Student Name
- Department
- Destination
- Reason
- Departure Date
- Departure Time
- Expected Return
- Status
- Action

Actions:

- View
- Approve
- Reject

Use clear status indicators:

PENDING
APPROVED
REJECTED

==================================================
## GATE PASS DETAILS
==================================================

When the HOD selects a request, show a detailed view.

Display:

Student information
Gate-pass information
Reason
Destination
Departure time
Expected return time
Previous relevant information if available

Buttons:

APPROVE
REJECT
BACK

When approving:

Show a confirmation dialog.

When rejecting:

Open a rejection dialog requiring:

- Rejection reason

Do not allow an empty rejection reason.

Mock service functions:

get_pending_gatepasses()
get_gatepass_details(id)
approve_gatepass(id)
reject_gatepass(id, reason)

Future API operations:

GET /api/gatepasses/pending
GET /api/gatepasses/{id}
PATCH /api/gatepasses/{id}/approve
PATCH /api/gatepasses/{id}/reject

==================================================
## SCREEN 4 — NOTIFICATIONS
==================================================

Allow the HOD to publish notifications.

Fields:

- Notification title
- Message
- Audience
- Priority
- Expiration date

Possible audience:

- Department
- All Students
- Specific group

Actions:

- Publish
- Clear

Below the form, show previously published notifications.

Columns:

- Title
- Audience
- Created
- Status

Future API:

POST /api/notifications
GET /api/notifications/created-by-me

==================================================
## SCREEN 5 — ATTENDANCE
==================================================

Create an attendance viewing interface.

The HOD should be able to filter by:

- Department
- Semester
- Section
- Subject
- Date range

Display:

- Student ID
- Student Name
- Subject
- Classes Held
- Present
- Absent
- Attendance %

Include visual status indicators.

Example:

90%+       Good
75–89%     Normal
Below 75%  Attention

These thresholds are UI presentation rules only.

The eventual backend should provide the authoritative attendance calculations.

Future API:

GET /api/attendance/department
GET /api/attendance/student/{id}
GET /api/attendance/summary

==================================================
## SCREEN 6 — ANALYTICS
==================================================

Create a departmental analytics dashboard.

Include:

- Average attendance
- Attendance distribution
- Students below threshold
- Subject-wise attendance
- Semester-wise attendance

Use charts where appropriate.

Since this is Tkinter, use an appropriate charting solution or create clean visual summaries without adding unnecessary dependencies.

Keep the analytics implementation modular so the source can later be replaced with real API data.

Future API:

GET /api/analytics/department/attendance
GET /api/analytics/department/subjects

==================================================
## SCREEN 7 — REPORTS
==================================================

Create a reports section.

Possible report types:

- Department Attendance Report
- Student Attendance Report
- Gate Pass Report
- Notification Report

At Stage 1, report generation can be mocked or demonstrate sample report generation.

Do not implement backend report storage.

Future API integration should be possible.

==================================================
## MOCK DATA
==================================================

Create realistic mock data for:

- HOD
- Students
- Gate-pass requests
- Attendance
- Notifications
- Analytics

Do not scatter mock data through UI code.

Create a dedicated mock-data/service layer.

==================================================
## PROJECT STRUCTURE
==================================================

Use a modular structure similar to:

hod_desktop/
│
├── main.py
│
├── config/
│   └── settings.py
│
├── models/
│   ├── student.py
│   ├── gatepass.py
│   ├── notification.py
│   └── attendance.py
│
├── services/
│   ├── auth_service.py
│   ├── gatepass_service.py
│   ├── notification_service.py
│   ├── attendance_service.py
│   └── analytics_service.py
│
├── mock/
│   └── mock_data.py
│
├── api/
│   └── api_client.py
│
├── ui/
│   ├── login.py
│   ├── dashboard.py
│   ├── gatepass.py
│   ├── notifications.py
│   ├── attendance.py
│   ├── analytics.py
│   └── reports.py
│
└── utils/
    └── helpers.py

You may modify this structure if a better modular design is justified.

==================================================
## API INTEGRATION BOUNDARY
==================================================

Create service functions that currently use mock data.

For example:

def get_pending_gatepasses():
    # Stage 1: return mock data
    # Stage 2: GET /api/gatepasses/pending

Do NOT directly call the future backend.

Create an API client abstraction that can later replace the mock implementation.

==================================================
## QUALITY REQUIREMENTS
==================================================

The application must:

- Start successfully
- Have working navigation
- Have functional forms
- Have functional mock interactions
- Have validation
- Have confirmation dialogs
- Have meaningful empty states
- Have clean error handling
- Have consistent styling
- Be modular
- Be readable
- Be easy to connect to the future FastAPI backend

Do not implement unnecessary features outside this specification.

==================================================
## FINAL DELIVERABLE
==================================================

Produce the complete HOD desktop prototype.

After implementation, explain:

1. Project structure
2. How to run it
3. Screens implemented
4. Mock data architecture
5. API integration points
6. What will need to change when the FastAPI backend is introduced
7. Any assumptions made


Do not make the UI dependent on mock data structures in a way that would require redesigning the UI when real API responses are introduced. Define data models/service interfaces first, then have both mock and future API implementations conform to those interfaces.
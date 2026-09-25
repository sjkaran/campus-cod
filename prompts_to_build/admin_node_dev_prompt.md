# SMART CAMPUS MANAGEMENT SYSTEM

# ADMIN DESKTOP APPLICATION — NODE DEVELOPMENT PROMPT

Use the previously provided "Smart Campus Management System — Master Development Prompt" as the global architecture and engineering specification.

You are now responsible ONLY for developing the Admin Desktop Application.

Do not develop the Student Web Application, Attendance Faculty Application, or HOD Application.

Do not implement the central backend or database.

The objective is to build a complete, polished, standalone Admin Desktop Application prototype using Python and Tkinter, while maintaining a clean architecture for later integration with the central FastAPI backend.

==================================================

1. NODE IDENTITY
   ==================================================

Node:

Admin Desktop Application

Primary user:

College Administrator / Campus Administrator.

Technology:

* Python
* Tkinter
* ttk

Use additional Python packages only where they provide clear value.

The application should resemble a professional administrative management system rather than a basic Tkinter demonstration.

The Admin application is an internal college-management application and should prioritize:

* Information density
* Efficient navigation
* Tables
* Search and filtering
* Dashboard analytics
* Administrative workflows
* Clear status indicators
* Data validation
* Professional visual hierarchy

==================================================
2. ADMIN ROLE
=============

The Admin is responsible for system-level campus administration.

The Admin can:

* Log in
* View the administrative dashboard
* View and search student information
* View student attendance
* View attendance statistics
* View system-wide analytics
* Publish campus notifications
* View previously published notifications
* View gate-pass information
* Generate/view reports
* Manage appropriate administrative information
* Log out

The Admin should NOT automatically have HOD-specific approval authority unless explicitly defined by the system's authorization model.

The application should distinguish between:

ADMIN

and:

HOD

They are different roles.

==================================================
3. CURRENT DEVELOPMENT PHASE
============================

This is Stage 1.

Do NOT implement:

* PostgreSQL
* FastAPI
* Real authentication
* JWT
* Real REST API communication
* Database queries
* Server-side authorization
* Production deployment

Instead:

* Use realistic mock data.
* Create service abstractions.
* Create an API client boundary.
* Keep mock data separate from UI.
* Design all services so they can later be replaced with API implementations.

Architecture:

Tkinter UI
↓
Service Layer
↓
Mock Service

Later:

Tkinter UI
↓
Service Layer
↓
API Client
↓
FastAPI
↓
PostgreSQL

The UI must not directly access the database.

==================================================
4. APPLICATION LAYOUT
=====================

Create a professional desktop dashboard layout.

Recommended structure:

┌──────────────────────────────────────────────────────────────┐
│ Smart Campus Admin                         Admin: [Name]     │
├────────────────┬─────────────────────────────────────────────┤
│                │                                             │
│ Dashboard      │                                             │
│                │                                             │
│ Students       │                                             │
│                │                                             │
│ Attendance     │             MAIN CONTENT                    │
│                │                                             │
│ Notifications  │                                             │
│                │                                             │
│ Gate Passes    │                                             │
│                │                                             │
│ Analytics      │                                             │
│                │                                             │
│ Reports        │                                             │
│                │                                             │
│ Settings       │                                             │
│                │                                             │
│ Logout         │                                             │
└────────────────┴─────────────────────────────────────────────┘

Use a persistent sidebar/navigation panel and a main content area.

The application should support appropriate window resizing.

==================================================
5. LOGIN SCREEN
===============

Create an Admin login screen.

Fields:

* Admin ID / Username
* Password

Controls:

* Login
* Show/hide password

Include:

* Empty-field validation
* Invalid-credentials state
* Loading state
* Appropriate error messages

Stage 1 may use mock credentials.

Do not implement real authentication.

Create:

authenticate_admin(username, password)

Stage 1:

authenticate_admin()
↓
MockAuthService

Stage 2:

authenticate_admin()
↓
ApiAuthService
↓
POST /api/auth/login

After successful authentication:

Login
↓
Admin Dashboard

Logout:

Admin Application
↓
Login

==================================================
6. ADMIN DASHBOARD
==================

The dashboard is the central administrative overview.

It should provide a high-level view of the current campus state.

Include KPI/statistic cards.

Recommended metrics:

* Total Students
* Active Students
* Average Attendance
* Pending Gate Passes
* Today's Attendance
* Notifications Published

Example:

┌──────────────────┐ ┌──────────────────┐
│ Total Students   │ │ Avg Attendance   │
│     2,540        │ │      84.7%       │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ Pending Passes   │ │ Today's Presence │
│       34         │ │      91.2%       │
└──────────────────┘ └──────────────────┘

Below the KPI cards, include:

* Recent notifications
* Recent gate-pass activity
* Attendance summary
* Important system information

Use mock data.

Future API:

GET /api/admin/dashboard

==================================================
7. STUDENT MANAGEMENT
=====================

Create a dedicated Students section.

The Admin should be able to view student records.

Display a table containing:

* Student ID
* Name
* Roll Number
* Department
* Semester
* Section
* Email
* Status

Possible status:

ACTIVE
INACTIVE

Provide:

* Search
* Department filter
* Semester filter
* Section filter
* Status filter

Search should support useful fields such as:

* Student ID
* Name
* Roll number

Do not create unnecessary editing capabilities unless explicitly required.

The initial version should focus on viewing and searching student records.

==================================================
8. STUDENT DETAILS
==================

When the Admin selects a student, show a detailed student view.

Display:

Personal information:

* Student ID
* Name
* Roll number
* Email
* Department
* Semester
* Section
* Status

Academic overview:

* Overall attendance
* Subjects
* Attendance warnings

Gate-pass summary:

* Total requests
* Approved
* Rejected
* Pending

Recent activity may include:

* Recent attendance
* Recent gate-pass requests
* Relevant notifications

Future API:

GET /api/students
GET /api/students/{id}
GET /api/students/{id}/attendance
GET /api/students/{id}/gatepasses

==================================================
9. ATTENDANCE MANAGEMENT
========================

Create an Attendance section.

The Admin should be able to inspect attendance across the institution.

Provide filters:

* Department
* Semester
* Section
* Subject
* Date
* Date range
* Attendance status

Display attendance records in a table.

Example:

Student ID | Name | Subject | Held | Present | Absent | %

ST001 | Rahul | AI | 40 | 36 | 4 | 90%
ST002 | Priya | AI | 40 | 31 | 9 | 77.5%

Provide sorting where appropriate.

The interface should allow the Admin to identify:

* Students with low attendance
* Subjects with low attendance
* Departments with low attendance

The Admin should not directly modify attendance unless this is explicitly added to the authorization model.

This node is primarily an administrative monitoring interface.

Future API:

GET /api/attendance
GET /api/attendance/summary
GET /api/attendance/students/{id}

==================================================
10. ATTENDANCE SUMMARY
======================

Create an attendance summary area.

Display:

* Institution average attendance
* Department averages
* Semester averages
* Number of students below threshold
* Number of students critically below threshold

Example:

Overall Attendance: 84.7%

Students below threshold: 143

Students critically below threshold: 27

Use clear visual indicators.

The threshold must eventually be configurable by the backend.

Do not hard-code institutional rules into multiple UI components.

For Stage 1, use mock configuration.

==================================================
11. NOTIFICATION MANAGEMENT
===========================

The Admin should be able to publish campus notifications.

Create a notification composition interface.

Fields:

* Title
* Message
* Audience
* Priority
* Publish date/time
* Expiration date

Audience options may include:

* All Students
* Department
* Semester
* Section
* Specific Student Group

Priority:

* Normal
* Important
* Urgent

Actions:

* Preview
* Publish
* Clear

Before publishing, show a confirmation dialog.

Example:

"Publish this notification to 2,540 students?"

Buttons:

Cancel
Publish

Future API:

POST /api/notifications

==================================================
12. NOTIFICATION HISTORY
========================

Below the publishing interface, display notification history.

Columns:

* Notification ID
* Title
* Audience
* Priority
* Published By
* Published Date
* Expiration
* Status

Possible status:

ACTIVE
EXPIRED
DRAFT

If drafts are implemented, keep them as a UI prototype feature only unless backend support is later specified.

Provide:

* Search
* Filter by priority
* Filter by status
* Filter by audience

Future API:

GET /api/notifications/admin

==================================================
13. GATE-PASS MONITORING
========================

The Admin should be able to monitor gate-pass activity.

Important distinction:

The Admin is monitoring the gate-pass system.

The HOD is responsible for approval/rejection according to the defined role model.

Therefore, do not automatically give the Admin approval/rejection controls.

Display:

* Request ID
* Student ID
* Student name
* Department
* Destination
* Departure date
* Return date
* Status
* Submitted date
* Reviewing authority

Statuses:

PENDING
APPROVED
REJECTED

Provide filters:

* Department
* Status
* Date range
* Student ID

Future API:

GET /api/gatepasses
GET /api/gatepasses/{id}

==================================================
14. GATE-PASS DETAILS
=====================

Allow the Admin to open a gate-pass record.

Display:

* Request ID
* Student information
* Destination
* Reason
* Departure
* Return
* Submission time
* Current status
* Reviewing authority
* Remarks

The Admin should be able to inspect the record but should not automatically be allowed to approve or reject it.

==================================================
15. ANALYTICS DASHBOARD
=======================

Create a dedicated analytics section.

This should be one of the strongest parts of the Admin application.

Provide institution-level analytics such as:

### Student statistics

* Total students
* Students by department
* Students by semester
* Active/inactive students

### Attendance analytics

* Overall attendance
* Department-wise attendance
* Semester-wise attendance
* Subject-wise attendance
* Low-attendance students

### Gate-pass analytics

* Total requests
* Pending requests
* Approved requests
* Rejected requests

### Notification analytics

* Notifications published
* Active notifications
* Notifications by audience

Use appropriate visualizations.

Possible visualizations:

* Bar charts
* Line charts
* Pie/donut charts
* KPI cards
* Progress indicators

Avoid creating charts simply for decoration.

Every visualization should answer a useful administrative question.

Future API examples:

GET /api/analytics/overview

GET /api/analytics/attendance

GET /api/analytics/attendance/departments

GET /api/analytics/attendance/subjects

GET /api/analytics/gatepasses

==================================================
16. REPORTS
===========

Create a Reports section.

Possible report types:

1. Student report
2. Attendance report
3. Department attendance report
4. Gate-pass report
5. Notification report
6. System summary report

Allow the Admin to select:

* Report type
* Date range
* Department
* Semester
* Section

Provide:

* Generate
* Preview
* Export

During Stage 1, report generation may use mock data.

Do not build complex backend report-generation infrastructure.

The architecture should allow future API integration.

Future conceptual APIs:

GET /api/reports/attendance
GET /api/reports/students
GET /api/reports/gatepasses

==================================================
17. SETTINGS
============

Create a basic Settings section.

The prototype may contain:

* Admin profile information
* Application information
* Display preferences
* Session information

Do not create system-wide configuration controls unless explicitly specified.

Do not expose database settings or backend secrets.

==================================================
18. SEARCH AND FILTERING
========================

Administrative applications depend heavily on search and filtering.

Implement consistent filtering behavior.

Where appropriate, support:

* Text search
* Dropdown filters
* Date filters
* Status filters
* Clear filters

Tables should update cleanly when filters change.

Provide an empty state when no results exist.

Example:

"No students match the selected filters."

==================================================
19. TABLE DESIGN
================

Use tables extensively where data is naturally tabular.

Tables should have:

* Clear column headers
* Appropriate column widths
* Row spacing
* Status badges
* Sorting where useful
* Selection behavior
* Scrollbars where required

Avoid excessively wide tables.

For detailed records, allow the user to open a dedicated detail view instead of displaying every field in the table.

==================================================
20. UI STATES
=============

Every major data-driven screen should support:

Loading
Success
Empty
Error

Examples:

Loading students...

No students found.

Unable to load attendance data.

Try Again

Although Stage 1 uses local mock data, design these states as if API requests are asynchronous.

==================================================
21. CONFIRMATION AND DESTRUCTIVE ACTIONS
========================================

Any potentially consequential action should use confirmation.

Examples:

* Publishing an important notification
* Logging out
* Future administrative destructive actions

For publishing:

"Are you sure you want to publish this notification?"

Do not make consequential operations happen accidentally from a single click.

==================================================
22. MOCK DATA
=============

Create realistic mock data for:

* Admin
* Students
* Attendance
* Subjects
* Departments
* Gate passes
* Notifications
* Analytics

Example student:

{
"id": "STU001",
"name": "Rahul Sharma",
"rollNumber": "CSE23001",
"department": "Computer Science",
"semester": 6,
"section": "A",
"email": "[rahul@example.com](mailto:rahul@example.com)",
"status": "ACTIVE"
}

Example attendance:

{
"studentId": "STU001",
"subject": "Artificial Intelligence",
"classesHeld": 40,
"present": 36,
"absent": 4,
"percentage": 90.0
}

Example gate pass:

{
"id": "GP001",
"studentId": "STU001",
"studentName": "Rahul Sharma",
"destination": "Home",
"status": "PENDING",
"submittedAt": "..."
}

Example notification:

{
"id": "N001",
"title": "Semester Examination Schedule",
"audience": "ALL_STUDENTS",
"priority": "IMPORTANT",
"status": "ACTIVE"
}

Mock data must not be embedded directly inside UI classes.

==================================================
23. SERVICE LAYER
=================

Create service abstractions such as:

authenticateAdmin()

getDashboardData()

getStudents()

getStudentDetails(studentId)

getAttendance()

getAttendanceSummary()

getNotifications()

publishNotification(data)

getGatePasses()

getGatePassDetails(gatePassId)

getAnalytics()

generateReport(parameters)

Stage 1:

UI
↓
Service
↓
Mock implementation

Stage 2:

UI
↓
Service
↓
API client
↓
FastAPI

The UI must not know whether the data comes from mock data or the network.

==================================================
24. API CLIENT BOUNDARY
=======================

Create a centralized API client abstraction.

For example:

apiClient

It should eventually be responsible for:

* Base URL
* HTTP requests
* Headers
* Authentication token
* Error handling
* Response handling

During Stage 1, it does not need to communicate with a real server.

Do not scatter future API URLs across Tkinter UI code.

==================================================
25. FUTURE API CONTRACT
=======================

Design the application around these conceptual endpoints.

Authentication:

POST /api/auth/login

Dashboard:

GET /api/admin/dashboard

Students:

GET /api/students
GET /api/students/{id}

Attendance:

GET /api/attendance
GET /api/attendance/summary
GET /api/attendance/students/{id}

Notifications:

GET /api/notifications/admin
POST /api/notifications

Gate Pass:

GET /api/gatepasses
GET /api/gatepasses/{id}

Analytics:

GET /api/analytics/overview
GET /api/analytics/attendance
GET /api/analytics/gatepasses

Reports:

GET /api/reports/students
GET /api/reports/attendance
GET /api/reports/gatepasses

These endpoints represent the future integration contract conceptually.

The exact backend contract may change.

Do not tightly couple individual UI components to raw API response structures.

==================================================
26. PROJECT STRUCTURE
=====================

Use a modular project structure similar to:

admin_desktop/
│
├── main.py
│
├── config/
│   └── settings.py
│
├── models/
│   ├── admin.py
│   ├── student.py
│   ├── attendance.py
│   ├── notification.py
│   ├── gatepass.py
│   └── analytics.py
│
├── services/
│   ├── auth_service.py
│   ├── dashboard_service.py
│   ├── student_service.py
│   ├── attendance_service.py
│   ├── notification_service.py
│   ├── gatepass_service.py
│   ├── analytics_service.py
│   └── report_service.py
│
├── api/
│   └── api_client.py
│
├── mock/
│   ├── students.py
│   ├── attendance.py
│   ├── notifications.py
│   ├── gatepasses.py
│   └── analytics.py
│
├── ui/
│   ├── login.py
│   ├── dashboard.py
│   ├── students.py
│   ├── attendance.py
│   ├── notifications.py
│   ├── gatepasses.py
│   ├── analytics.py
│   ├── reports.py
│   └── settings.py
│
└── utils/
├── validators.py
├── formatters.py
└── helpers.py

You may improve this structure if necessary, but preserve separation between:

UI
Models
Services
API
Mock data
Utilities

==================================================
27. SECURITY ARCHITECTURE
=========================

Do not implement production authentication in Stage 1.

However, design for:

* JWT authentication
* Role-based access control
* Session expiration
* Backend authorization
* Secure API communication

The Admin frontend must never contain:

* Database credentials
* Backend secrets
* Private keys
* Hard-coded production credentials

The frontend should not be considered an authorization boundary.

The eventual FastAPI backend must independently verify that the authenticated user has Admin privileges.

==================================================
28. ROLE SEPARATION
===================

Keep these roles distinct:

STUDENT
FACULTY
HOD
ADMIN

Do not implement functionality simply because another node has it.

For example:

Student:
Apply for gate pass.

HOD:
Approve/reject gate pass.

Admin:
Monitor gate-pass activity.

Faculty:
Submit attendance.

Admin:
Monitor attendance.

This separation must be reflected in the Admin UI.

==================================================
29. PERFORMANCE AND USABILITY
=============================

The application should remain responsive when displaying large mock datasets.

Do not create thousands of individual Tkinter widgets unnecessarily.

For tables:

* Use efficient tree/table structures.
* Use scrolling.
* Use pagination or simulated pagination if appropriate.
* Keep filtering efficient.

The application should feel like an operational administrative tool.

==================================================
30. ACCEPTANCE CRITERIA
=======================

The Admin Desktop Application is complete for Stage 1 when:

1. The application launches successfully.
2. Admin login works with mock credentials.
3. Dashboard displays meaningful system statistics.
4. Student records can be viewed.
5. Students can be searched.
6. Student records can be filtered.
7. Student details can be opened.
8. Attendance can be viewed.
9. Attendance can be filtered.
10. Attendance statistics are displayed.
11. Notifications can be created in the prototype.
12. Notification publishing has confirmation.
13. Notification history can be viewed.
14. Gate-pass records can be viewed.
15. Gate-pass records can be filtered.
16. Gate-pass details can be opened.
17. Admin does not receive HOD approval controls.
18. Analytics dashboard works using mock data.
19. Reports section works as a prototype.
20. Loading states exist.
21. Empty states exist.
22. Error states exist.
23. Search and filtering behave correctly.
24. Navigation works consistently.
25. Logout works.
26. Mock data is isolated from UI code.
27. Services are isolated from UI code.
28. Future API boundaries are clearly defined.
29. No database is accessed by the desktop application.
30. No backend implementation is included.
31. The project can later replace mock services with real API services without redesigning the application.

==================================================
31. FINAL OUTPUT REQUIRED
=========================

After implementation, provide:

1. Complete project structure.
2. Explanation of each major module.
3. Instructions for installing dependencies.
4. Instructions for running the application.
5. Mock Admin credentials.
6. List of all implemented screens.
7. List of all implemented workflows.
8. Explanation of the mock-data architecture.
9. Explanation of the service layer.
10. Explanation of the API integration boundary.
11. List of future API endpoints.
12. Explanation of where mock services will eventually be replaced by real API calls.
13. Explanation of role separation between Admin and HOD.
14. Known limitations.
15. Assumptions made.

==================================================
FINAL DEVELOPMENT PRINCIPLE
===========================

Build the Admin Desktop Application as a serious administrative client.

The application must be fully usable with mock data during Stage 1.

At the same time, it must remain independent of the backend and database.

The UI must communicate through a service abstraction.

Mock services are temporary.

The future FastAPI backend is the authoritative source of data and business rules.

Do not compromise the architecture merely to make the prototype appear functional.

The goal is:

POLISHED ADMIN UI
+
CLEAN SOFTWARE ARCHITECTURE
+
CLEAR API BOUNDARY
+
EASY FUTURE INTEGRATION

# SMART CAMPUS MANAGEMENT SYSTEM

# STUDENT WEB APPLICATION — NODE DEVELOPMENT PROMPT

Use the previously provided "Smart Campus Management System — Master Development Prompt" as the global architecture and engineering specification.

You are now responsible ONLY for developing the Student Web Application.

Do not develop the Admin, Faculty, or HOD applications.

Do not implement the central backend or database.

The current objective is to build a complete, polished, standalone Student Web Application prototype whose UI and internal architecture are ready for later integration with the central FastAPI backend.

==================================================

1. NODE IDENTITY
   ==================================================

Node:

Student Web Application

Primary users:

Students of the college.

Technology:

* HTML
* CSS
* JavaScript

You may use a lightweight frontend library/framework only if it provides a clear benefit, but do not introduce unnecessary complexity.

The application should be designed as a modern college/campus portal rather than a generic CRUD website.

The final application should feel like a real product that students would use regularly.

==================================================
2. STUDENT ROLE
===============

The student is a regular campus user.

The student can:

* Log in
* View a personal dashboard
* View campus notifications
* View attendance
* View attendance statistics
* Apply for a gate pass
* View submitted gate-pass requests
* Track gate-pass status
* View profile information
* Log out

The student must NOT have access to:

* Administrative controls
* Student management
* Attendance submission
* Attendance modification
* Gate-pass approval/rejection
* System analytics intended for administrators
* HOD controls
* Faculty controls

The frontend should only expose functionality relevant to the student role.

However, remember that UI restrictions are NOT security.

The eventual backend will enforce authorization.

==================================================
3. CURRENT DEVELOPMENT PHASE
============================

This is Stage 1 of the project.

Do NOT implement:

* PostgreSQL
* FastAPI
* Real authentication
* JWT
* Real API requests
* Real database queries
* Server-side business logic

Instead:

* Use realistic mock data.
* Create an API/service abstraction layer.
* Make all data operations go through that abstraction.
* Clearly isolate mock implementations.
* Design the interfaces so they can later be replaced by real API calls.

The final architecture should conceptually be:

Student UI
↓
Frontend service/API layer
↓
Mock implementation

Later:

Student UI
↓
Frontend service/API layer
↓
REST API
↓
FastAPI backend
↓
PostgreSQL

The UI should require minimal or no restructuring when the real API is introduced.

==================================================
4. APPLICATION INFORMATION ARCHITECTURE
=======================================

The main navigation should contain:

* Dashboard
* Notifications
* Attendance
* Gate Pass
* Profile
* Logout

The primary application layout should be:

┌─────────────────────────────────────────────────────────────┐
│ Smart Campus                         Student Name     [⌄]    │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│ Dashboard    │                                              │
│              │                                              │
│ Notifications│              MAIN CONTENT                    │
│              │                                              │
│ Attendance   │                                              │
│              │                                              │
│ Gate Pass    │                                              │
│              │                                              │
│ Profile      │                                              │
│              │                                              │
│ Logout       │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘

The exact layout may be improved if a better responsive design is appropriate.

For mobile/smaller screens, the sidebar may transform into a navigation menu.

==================================================
5. LOGIN PAGE
=============

Create a professional student login page.

The page should contain:

* Smart Campus branding
* Student ID / username field
* Password field
* Show/hide password control
* Login button
* Appropriate validation
* Error state
* Loading state

Do not implement real authentication.

Use mock authentication.

Example mock credentials can be provided for demonstration.

The authentication operation must be isolated behind a service.

Conceptually:

loginStudent(username, password)

Stage 1:

loginStudent()
↓
MockAuthService

Stage 2:

loginStudent()
↓
ApiAuthService
↓
POST /api/auth/login

After successful login:

Login
↓
Student Dashboard

After logout:

Application
↓
Login page

Do not store real passwords anywhere in the frontend.

==================================================
6. STUDENT DASHBOARD
====================

The dashboard is the primary landing page after login.

It should provide a concise overview of the student's current campus status.

Include:

A. Welcome section

Example:

"Good morning, Karan."

Below it:

"Here's your campus overview."

Use the student's mock profile information.

B. Attendance summary

Display:

* Overall attendance percentage
* Classes attended
* Classes missed
* Total classes

Example:

┌──────────────────────────────┐
│ Overall Attendance           │
│                              │
│          84.6%               │
│                              │
│ 34 Present / 40 Classes      │
└──────────────────────────────┘

Use an appropriate visual representation such as:

* Progress ring
* Progress bar
* Percentage indicator

C. Gate-pass status

Show:

* Pending requests
* Approved requests
* Rejected requests

Example:

Pending Gate Passes: 1

D. Recent notifications

Display the latest 3–5 notifications.

Each notification should show:

* Title
* Short message
* Date/time
* Priority/status if appropriate

Provide:

"View all notifications"

E. Quick actions

Provide convenient actions:

* View Attendance
* Apply for Gate Pass
* View Notifications

The dashboard should not become overloaded with information.

==================================================
7. NOTIFICATIONS PAGE
=====================

Create a dedicated notifications page.

The student should be able to view campus notifications relevant to them.

Each notification should contain:

* Title
* Message
* Published date/time
* Publisher
* Audience/category
* Priority
* Read/unread state

Example:

┌─────────────────────────────────────────────────────────────┐
│ Examination Schedule Released                               │
│ Academic Office                                             │
│ 23 September 2026                                           │
│                                                             │
│ The semester examination schedule has been published...     │
│                                                             │
│ [Read]                                                      │
└─────────────────────────────────────────────────────────────┘

Support:

* Unread indicator
* Read state
* Notification filtering if useful
* Search if appropriate
* Empty state

Example empty state:

"No new notifications."

The student should NOT be able to create, edit, or delete notifications.

Future API:

GET /api/notifications

Possible future operation:

PATCH /api/notifications/{id}/read

The current implementation should use mock notification data.

==================================================
8. ATTENDANCE PAGE
==================

Create a comprehensive attendance section.

The page should provide both summary information and detailed attendance records.

A. Overall attendance

Display:

* Overall percentage
* Total classes
* Present
* Absent

B. Subject-wise attendance

Create a table:

Subject | Classes | Present | Absent | Attendance %

Example:

Artificial Intelligence | 40 | 35 | 5 | 87.5%
Database Systems        | 38 | 31 | 7 | 81.6%
Operating Systems       | 42 | 36 | 6 | 85.7%

Use visual status indicators.

C. Attendance history

Provide a detailed table:

Date | Subject | Session | Status

Example:

23 Sep | AI | Morning | Present
22 Sep | DBMS | Afternoon | Absent
21 Sep | OS | Morning | Present

Support filtering by:

* Subject
* Date range
* Attendance status

D. Attendance warning

If attendance is below the configured threshold, display an informative warning.

Example:

"Your attendance in Database Systems is below the required threshold."

Do not hard-code institutional policy into the frontend.

The threshold should eventually come from backend configuration.

For Stage 1, use a mock configuration value.

Future API examples:

GET /api/students/me/attendance
GET /api/students/me/attendance/subjects
GET /api/students/me/attendance/history

==================================================
9. GATE PASS PAGE
=================

This is one of the most important student workflows.

The page should contain two major sections:

1. Apply for Gate Pass
2. Gate Pass History

---

## 9.1 APPLY FOR GATE PASS

Create a form containing:

* Destination
* Reason
* Departure date
* Departure time
* Expected return date
* Expected return time
* Additional remarks if necessary

The form must validate:

* Required fields
* Valid dates
* Valid times
* Logical departure/return relationship
* Reason length
* Destination length

Do not allow obviously invalid submissions.

When the student clicks Submit:

Show a confirmation step.

Example:

"Are you sure you want to submit this gate-pass request?"

Buttons:

Cancel
Confirm Submission

After submission:

Show success feedback.

Example:

"Gate-pass request submitted successfully."

The request should initially have:

Status = PENDING

Future API:

POST /api/gatepasses

Mock service:

submitGatePass(data)

---

## 9.2 GATE PASS HISTORY

Display previously submitted requests.

Table/card information:

* Request ID
* Destination
* Reason
* Departure
* Return
* Submitted date
* Status

Possible statuses:

PENDING
APPROVED
REJECTED

Use visually distinct status indicators.

When a request is rejected, display the rejection reason if available.

Example:

Status: REJECTED

Reason:

"Insufficient information provided."

The student cannot approve or modify the request after submission unless such functionality is explicitly introduced later.

Future API:

GET /api/gatepasses/my

GET /api/gatepasses/{id}

==================================================
10. GATE PASS DETAILS
=====================

Allow the student to open an individual gate-pass request.

Display:

* Request ID
* Student information
* Destination
* Reason
* Departure date/time
* Expected return date/time
* Submission timestamp
* Current status
* HOD remarks/rejection reason if applicable

Provide a clear status timeline if appropriate:

Submitted
↓
Under Review
↓
Approved

or:

Submitted
↓
Under Review
↓
Rejected

This is a UI representation only.

The backend will eventually determine the authoritative status.

==================================================
11. PROFILE PAGE
================

Create a student profile page.

Display:

* Student ID
* Name
* Email
* Phone if appropriate
* Department
* Semester
* Section
* Roll number
* Admission/academic information if appropriate

The student should be able to view their profile.

Do not implement sensitive profile editing unless explicitly required.

If editing is included, clearly separate editable and read-only fields.

Future API:

GET /api/students/me

==================================================
12. NAVIGATION AND STATE
========================

Navigation should be predictable.

Recommended flow:

Login
↓
Dashboard
├── Notifications
├── Attendance
├── Gate Pass
└── Profile

The application should preserve appropriate UI state while navigating.

For example:

* Selected attendance filter
* Current notification state
* Gate-pass form validation state

Do not unnecessarily reload or recreate the entire interface during normal navigation.

==================================================
13. RESPONSIVE DESIGN
=====================

The application is primarily a web application.

It must work properly on:

* Desktop
* Laptop
* Tablet
* Smaller screens

Use responsive CSS.

The desktop version should use a sidebar/navigation layout.

On smaller screens:

* Collapse the sidebar
* Use a menu button or suitable mobile navigation
* Make tables horizontally scrollable where necessary
* Avoid content overflowing the viewport

Do not simply shrink everything.

Maintain usability.

==================================================
14. VISUAL DESIGN
=================

Use a professional campus-management visual language.

Design goals:

* Clean
* Modern
* Minimal
* Professional
* Information-oriented
* Accessible

Use consistent:

* Typography
* Spacing
* Border radius
* Shadows
* Buttons
* Form controls
* Cards
* Tables
* Status badges

Suggested visual hierarchy:

Primary content
↓
Secondary information
↓
Metadata

Avoid excessive gradients, animations, glassmorphism, decorative elements, or visual effects that do not improve usability.

Animations should be subtle and purposeful.

==================================================
15. LOADING STATES
==================

Even though Stage 1 uses mock data, design the application as if network requests exist.

Every data-driven section should be capable of displaying:

Loading
↓
Success
↓
Empty
↓
Error

Examples:

Loading attendance...

No attendance records found.

Unable to load attendance data. Please try again.

This will make later API integration much easier.

==================================================
16. ERROR HANDLING
==================

Create user-friendly error states.

Do not expose raw JavaScript errors to users.

For example, avoid:

"TypeError: Cannot read properties of undefined..."

Instead:

"Something went wrong while loading your attendance."

Provide a retry option where appropriate.

==================================================
17. MOCK DATA ARCHITECTURE
==========================

Create realistic mock data.

Example student:

{
id: "STU-2026-001",
name: "Karan",
department: "Computer Science",
semester: 6,
section: "A",
email: "[student@example.com](mailto:student@example.com)"
}

Example notification:

{
id: "N001",
title: "Examination Schedule Released",
message: "...",
publisher: "Academic Office",
createdAt: "...",
priority: "normal",
read: false
}

Example gate pass:

{
id: "GP001",
destination: "Home",
reason: "Personal work",
departureDate: "...",
departureTime: "...",
returnDate: "...",
returnTime: "...",
status: "PENDING"
}

Example attendance:

{
subject: "Artificial Intelligence",
totalClasses: 40,
present: 35,
absent: 5,
percentage: 87.5
}

Do not scatter these objects throughout the application.

Create a dedicated mock-data/service layer.

==================================================
18. SERVICE/API ABSTRACTION
===========================

The UI must not directly manipulate mock arrays.

Create service functions such as:

loginStudent()
getCurrentStudent()
getNotifications()
markNotificationAsRead()
getAttendanceSummary()
getSubjectAttendance()
getAttendanceHistory()
submitGatePass()
getMyGatePasses()
getGatePassDetails()

Stage 1:

UI
↓
Service
↓
Mock Data

Stage 2:

UI
↓
Service
↓
HTTP/API Client
↓
FastAPI

The UI should not need to know whether the data came from mock data or the network.

==================================================
19. FUTURE API CONTRACT
=======================

Prepare the frontend around the following conceptual API endpoints.

Authentication:

POST /api/auth/login

Student:

GET /api/students/me

Notifications:

GET /api/notifications

PATCH /api/notifications/{id}/read

Attendance:

GET /api/students/me/attendance

GET /api/students/me/attendance/subjects

GET /api/students/me/attendance/history

Gate Pass:

POST /api/gatepasses

GET /api/gatepasses/my

GET /api/gatepasses/{id}

The exact API contract may change during backend development.

Therefore, do not tightly couple UI components to raw HTTP responses.

Use a service/API client layer.

==================================================
20. SECURITY CONSIDERATIONS
===========================

Do not treat frontend restrictions as security.

The eventual backend will enforce:

* Authentication
* Authorization
* Student ownership of data
* Gate-pass access restrictions
* Notification access
* Attendance access

The frontend should nevertheless avoid exposing administrative operations.

Do not place:

* Database credentials
* API secrets
* Private keys
* Administrative credentials

inside frontend source code.

==================================================
21. PROJECT STRUCTURE
=====================

Use a clean modular structure.

A suitable structure is:

student-web/
│
├── index.html
├── package.json
│
├── public/
│   └── assets/
│
└── src/
│
├── components/
│   ├── Navbar/
│   ├── Sidebar/
│   ├── StatCard/
│   ├── NotificationCard/
│   ├── StatusBadge/
│   ├── AttendanceTable/
│   └── GatePassCard/
│
├── pages/
│   ├── Login/
│   ├── Dashboard/
│   ├── Notifications/
│   ├── Attendance/
│   ├── GatePass/
│   └── Profile/
│
├── services/
│   ├── authService.js
│   ├── studentService.js
│   ├── notificationService.js
│   ├── attendanceService.js
│   └── gatePassService.js
│
├── api/
│   └── apiClient.js
│
├── mock/
│   ├── students.js
│   ├── notifications.js
│   ├── attendance.js
│   └── gatePasses.js
│
├── models/
│   └── models.js
│
├── styles/
│   ├── global.css
│   └── variables.css
│
└── utils/
├── validation.js
├── formatting.js
└── constants.js

You may modify this structure if the selected frontend technology requires a different organization, but preserve the same separation of concerns.

==================================================
22. IMPORTANT ARCHITECTURAL RESTRICTIONS
========================================

Do NOT:

* Build the FastAPI backend.
* Build the database.
* Connect directly to PostgreSQL.
* Put database logic in the frontend.
* Hard-code API URLs throughout components.
* Hard-code student information into UI components.
* Implement administrative functionality.
* Implement HOD approval functionality.
* Implement faculty attendance submission.
* Recreate the QR attendance system.
* Assume the final database schema is fixed.
* Create unnecessary microservices.
* Overengineer the application.

The current objective is the Student Web Node.

==================================================
23. ACCEPTANCE CRITERIA
=======================

The Student Web Application will be considered complete for Stage 1 when:

1. The application starts successfully.
2. The student can log in using mock credentials.
3. The student reaches a functional dashboard.
4. Notifications can be viewed.
5. Notification read/unread states work in the prototype.
6. Attendance summary is displayed.
7. Subject-wise attendance is displayed.
8. Attendance history can be viewed and filtered.
9. A student can submit a gate-pass request.
10. Form validation works.
11. Submitted gate passes appear in history.
12. Gate-pass status is displayed.
13. Gate-pass details can be opened.
14. Rejection remarks can be displayed.
15. Student profile can be viewed.
16. Logout works.
17. Loading states exist.
18. Empty states exist.
19. Error states exist.
20. The application is responsive.
21. Mock data is isolated from UI components.
22. Future API operations are isolated behind a service/API layer.
23. No database access exists in the frontend.
24. No backend implementation is included.
25. The project can later replace mock services with real API services without redesigning the UI.

==================================================
24. FINAL OUTPUT REQUIRED FROM THE CODING AI
============================================

After completing the implementation, provide:

1. Complete project structure.
2. Explanation of every major module.
3. Instructions to install dependencies.
4. Instructions to run the application.
5. Mock credentials.
6. List of implemented screens.
7. List of implemented student workflows.
8. Description of the mock-data architecture.
9. Description of the API abstraction layer.
10. List of future API endpoints required.
11. Explanation of exactly where real API integration should replace mock implementations.
12. Any assumptions made during development.
13. Any known limitations.

FINAL PRINCIPLE:

Build a polished, production-style Student Web Application prototype now.

Keep the backend boundary clean.

Use mock data now.

Design every data operation so that it can later be replaced by a REST API.

Do not let the absence of the backend compromise the quality of the frontend architecture.

The final Student Web Application should look complete to a user while remaining deliberately independent of the future backend and database.


Do not make the UI dependent on mock data structures in a way that would require redesigning the UI when real API responses are introduced. Define data models/service interfaces first, then have both mock and future API implementations conform to those interfaces.
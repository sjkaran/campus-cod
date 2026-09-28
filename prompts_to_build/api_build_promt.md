# SMART CAMPUS MANAGEMENT SYSTEM

# CENTRAL BACKEND + API DEVELOPMENT PROMPT

You are now responsible for developing the central backend and API system for the Smart Campus Management System.

The four client nodes have been/will be developed independently:

1. Student Web Application
2. Admin Desktop Application
3. Attendance Faculty Desktop Application
4. HOD Desktop Application

Your responsibility is to build the central backend that connects these four nodes and provides the authoritative application logic and data layer.

Do NOT rebuild the client interfaces.

Do NOT place business logic inside the clients that belongs in this backend.

The backend is the central source of truth for the entire system.

==================================================

1. SYSTEM ARCHITECTURE
   ==================================================

The final architecture is:

```
                     ┌─────────────────────┐
                     │     PostgreSQL      │
                     │      Database       │
                     └──────────▲──────────┘
                                │
                                │ SQLAlchemy
                                │
                     ┌──────────┴──────────┐
                     │    FastAPI Backend  │
                     │                     │
                     │ Authentication      │
                     │ Authorization       │
                     │ Students            │
                     │ Attendance          │
                     │ Gate Pass           │
                     │ Notifications       │
                     │ Analytics           │
                     │ Reports             │
                     │ Audit Logs          │
                     └──────────▲──────────┘
                                │
                          REST / JSON
                                │
          ┌─────────────────────┼──────────────────────┐
          │                     │                      │
          ▼                     ▼                      ▼
   Student Website        Admin Desktop          HOD Desktop
          │
          │
          └───────────────┐
                          │
                          ▼
                   Faculty Desktop
                          │
                          │
                   Existing QR System
```

```

The four clients must NEVER directly access PostgreSQL.

All persistent data operations must pass through the backend.

==================================================
2. PRIMARY TECHNOLOGY
==================================================

Use:

Backend:

- Python
- FastAPI
- Uvicorn

Database:

- PostgreSQL

ORM:

- SQLAlchemy

Validation:

- Pydantic

Authentication:

- JWT access tokens

Password hashing:

- Argon2 or bcrypt

Testing:

- pytest
- FastAPI TestClient

Configuration:

- Environment variables
- `.env` for local development

Migrations:

- Alembic

Documentation:

- FastAPI OpenAPI/Swagger

HTTP:

- REST
- JSON

Do not introduce microservices.

Use a modular monolith.

==================================================
3. ARCHITECTURAL PRINCIPLE
==================================================

The backend should follow:

Router
   ↓
Schema validation
   ↓
Service / Business Logic
   ↓
Repository / Data Access
   ↓
SQLAlchemy
   ↓
PostgreSQL

Do NOT put all logic inside FastAPI route functions.

For example, avoid:

@app.post("/gatepasses")
def create_gatepass(...):
    # 200 lines of business logic
    # database operations
    # validation
    # notifications
    # etc.

Instead:

Router
   ↓
GatePassService
   ↓
Repository
   ↓
Database

The backend must remain maintainable as the project grows.

==================================================
4. CORE DOMAIN MODULES
==================================================

Create the following backend modules:

1. Authentication
2. Users
3. Students
4. Faculty
5. HOD
6. Admin
7. Departments
8. Subjects
9. Academic Classes
10. Attendance
11. Gate Pass
12. Notifications
13. Analytics
14. Reports
15. Audit Logs

Do not create unnecessary modules unless required.

==================================================
5. USER ROLES
==================================================

The system has four primary roles:

STUDENT
FACULTY
HOD
ADMIN

The backend must enforce role-based access control.

Do NOT rely on frontend UI restrictions for authorization.

For example:

Hiding the "Approve Gate Pass" button from the Admin interface does NOT mean the Admin is prohibited from calling the endpoint.

The backend must independently verify permissions.

==================================================
6. ROLE PERMISSION MODEL
==================================================

### STUDENT

Allowed:

- Login
- View own profile
- View own attendance
- View relevant notifications
- Create gate-pass request
- View own gate-pass requests
- View own gate-pass status

Not allowed:

- View other students' private data
- Modify attendance
- Approve gate passes
- Submit attendance
- Create administrative notifications
- View administrative analytics

--------------------------------------------------

### FACULTY

Allowed:

- Login
- View own profile
- View assigned subjects/classes
- Create attendance sessions
- Conduct attendance
- Submit finalized attendance
- View own attendance sessions
- View relevant attendance reports

Not allowed:

- Approve/reject gate passes unless explicitly authorized
- Modify arbitrary historical attendance
- Access system-wide administrative data

--------------------------------------------------

### HOD

Allowed:

- Login
- View departmental students
- View departmental attendance
- View departmental analytics
- View gate-pass requests within their authority
- Approve gate-pass requests
- Reject gate-pass requests
- Publish permitted notifications

--------------------------------------------------

### ADMIN

Allowed:

- Login
- View system-level student information
- View system-wide attendance
- View system-wide analytics
- Publish campus notifications
- Monitor gate-pass activity
- Generate administrative reports
- Perform permitted administrative operations

Admin and HOD must remain distinct roles.

==================================================
7. AUTHENTICATION
==================================================

Implement secure authentication.

Flow:

Client
   ↓
POST /api/auth/login
   ↓
Validate credentials
   ↓
Verify password hash
   ↓
Generate JWT
   ↓
Return access token
```

Login response should contain conceptually:

{
"access_token": "...",
"token_type": "bearer",
"user": {
"id": "...",
"role": "STUDENT"
}
}

Do not return password information.

Use secure password hashing.

Never store plaintext passwords.

==================================================
8. JWT
======

Implement:

* JWT access tokens
* Configurable expiration
* User ID claim
* Role claim
* Token validation

Do not hard-code:

* Secret key
* Production credentials
* Database password

Use environment variables.

Example:

JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=...

The exact production configuration can later be hardened.

==================================================
9. AUTHORIZATION
================

Create reusable authorization dependencies.

Conceptually:

get_current_user()

require_student()

require_faculty()

require_hod()

require_admin()

require_roles(...)

Example:

@app.post("/api/gatepasses/{id}/approve")
require_hod()

The actual implementation should use FastAPI dependency injection.

==================================================
10. DATABASE DESIGN
===================

Use PostgreSQL.

Create normalized relational models.

At minimum:

users
students
faculty
hods
admins
departments
subjects
academic_classes
attendance_sessions
attendance_records
gate_passes
notifications
notification_targets
audit_logs

You may introduce additional supporting tables where required.

==================================================
11. USERS TABLE
===============

Conceptual fields:

users

* id
* username
* password_hash
* role
* is_active
* created_at
* updated_at
* last_login

Role should be represented using an enum or equivalent controlled value.

Possible:

STUDENT
FACULTY
HOD
ADMIN

==================================================
12. STUDENTS
============

Conceptual:

students

* id
* user_id
* student_id
* roll_number
* name
* email
* phone
* department_id
* semester
* section
* status
* created_at
* updated_at

A student must belong to a department.

==================================================
13. FACULTY
===========

Conceptual:

faculty

* id
* user_id
* faculty_id
* name
* email
* department_id
* status

Faculty may be associated with subjects/classes.

==================================================
14. HOD
=======

Conceptual:

hods

* id
* user_id
* employee_id
* name
* department_id

The department relationship is important because HOD authorization should normally be scoped to the HOD's department.

==================================================
15. ADMIN
=========

Conceptual:

admins

* id
* user_id
* employee_id
* name
* status

Admin is institution-level unless further authorization rules are introduced.

==================================================
16. DEPARTMENTS
===============

departments

* id
* code
* name
* status

Example:

CSE
ECE
ME
CE

==================================================
17. SUBJECTS
============

subjects

* id
* code
* name
* department_id
* credits
* status

==================================================
18. ACADEMIC CLASSES
====================

Create a representation of academic groups.

Possible fields:

academic_classes

* id
* department_id
* semester
* section
* academic_year
* status

This should allow the system to identify:

CSE
Semester 6
Section A
Academic Year 2026–27

==================================================
19. ATTENDANCE ARCHITECTURE
===========================

Attendance is one of the most important backend modules.

The existing QR attendance system is responsible for capturing attendance.

The central backend is responsible for storing and exposing the finalized attendance.

Architecture:

QR System
↓
Faculty Attendance Node
↓
Finalize
↓
POST attendance submission
↓
FastAPI
↓
Validate
↓
Store
↓
PostgreSQL

The backend must NOT depend on the internal implementation of the QR system.

==================================================
20. ATTENDANCE SESSION
======================

Create an attendance_sessions table/model.

Conceptual fields:

* id
* external_session_id
* faculty_id
* subject_id
* academic_class_id
* date
* start_time
* end_time
* status
* created_at
* finalized_at
* submitted_at

Possible statuses:

DRAFT
ACTIVE
CLOSED
SUBMITTED
CANCELLED

The backend should validate state transitions.

Example:

DRAFT → ACTIVE
ACTIVE → CLOSED
CLOSED → SUBMITTED

Do not permit arbitrary transitions.

==================================================
21. ATTENDANCE RECORDS
======================

Create attendance_records.

Conceptual:

* id
* session_id
* student_id
* status
* marked_at
* created_at

Possible status:

PRESENT
ABSENT

The database should enforce uniqueness where appropriate.

For example:

A student should not have two attendance records for the same session.

Use an appropriate database constraint.

==================================================
22. ATTENDANCE SUBMISSION
=========================

Create:

POST /api/attendance/sessions/{session_id}/submit

Only authorized faculty should be able to submit their own sessions.

Before accepting:

Validate:

* Session exists
* Faculty owns/is authorized for session
* Session is eligible for submission
* Students belong to the relevant academic class
* Attendance records are valid
* Duplicate records do not exist
* Required fields exist

Then:

Finalize
↓
Persist
↓
Return submission status

Example response:

{
"success": true,
"session_id": "...",
"status": "SUBMITTED"
}

==================================================
23. ATTENDANCE RETRIEVAL
========================

Student:

GET /api/students/me/attendance

Faculty:

GET /api/attendance/sessions/my

GET /api/attendance/sessions/{id}

HOD:

GET /api/attendance/department

Admin:

GET /api/attendance

The response should be appropriately scoped.

A student must not be able to query another student's private attendance simply by changing an ID.

==================================================
24. ATTENDANCE CALCULATIONS
===========================

Attendance calculations should be centralized.

For example:

attendance_percentage =
present_classes / total_classes × 100

Do not duplicate this logic across:

* Student frontend
* Admin frontend
* HOD frontend
* Faculty frontend

The backend should provide authoritative calculated values.

Example:

{
"total_classes": 40,
"present": 34,
"absent": 6,
"percentage": 85.0
}

==================================================
25. GATE-PASS MODULE
====================

The gate-pass workflow is:

Student
↓
Submit request
↓
PENDING
↓
HOD reviews
├── APPROVED
└── REJECTED
↓
Student views result

Create:

gate_passes

Conceptual fields:

* id
* student_id
* destination
* reason
* departure_date
* departure_time
* return_date
* return_time
* status
* hod_id
* hod_remarks
* created_at
* reviewed_at

Possible status:

PENDING
APPROVED
REJECTED
CANCELLED

==================================================
26. CREATE GATE PASS
====================

Endpoint:

POST /api/gatepasses

Only authenticated students may create their own gate-pass requests.

Validate:

* Required fields
* Date
* Time
* Departure/return relationship
* Reason
* Destination

Initial status:

PENDING

Do not allow students to set:

* APPROVED
* REJECTED
* hod_id
* reviewed_at

Those are backend-controlled fields.

==================================================
27. GATE PASS RETRIEVAL
=======================

Student:

GET /api/gatepasses/my

GET /api/gatepasses/{id}

HOD:

GET /api/gatepasses/pending

GET /api/gatepasses/{id}

Admin:

GET /api/gatepasses

GET /api/gatepasses/{id}

Apply authorization and data-scoping rules.

==================================================
28. GATE PASS APPROVAL
======================

Endpoint:

PATCH /api/gatepasses/{id}/approve

Only authorized HOD users may approve.

Before approval:

* Verify HOD role
* Verify HOD belongs to appropriate department
* Verify gate pass is PENDING
* Record HOD
* Set status APPROVED
* Set reviewed_at

Use a transaction.

==================================================
29. GATE PASS REJECTION
=======================

Endpoint:

PATCH /api/gatepasses/{id}/reject

Only authorized HOD users may reject.

Require:

reason / remarks

Do not permit:

PENDING → REJECTED

without recording the reviewing authority and reason.

==================================================
30. NOTIFICATION MODULE
=======================

Create:

notifications

Conceptual fields:

* id
* title
* message
* created_by
* priority
* audience_type
* created_at
* expires_at
* status

Possible priority:

NORMAL
IMPORTANT
URGENT

Possible audience:

ALL_STUDENTS
DEPARTMENT
SEMESTER
SECTION
SPECIFIC_GROUP

==================================================
31. NOTIFICATION TARGETING
==========================

Notifications may eventually target:

All students
Department
Semester
Section
Specific groups

Do not simply duplicate the notification record for every student unless there is a strong reason.

Use an appropriate targeting mechanism.

Potential:

notification_targets

or another normalized relationship.

==================================================
32. NOTIFICATION ENDPOINTS
==========================

Student:

GET /api/notifications

Admin:

POST /api/notifications

GET /api/notifications/admin

HOD:

POST /api/notifications

GET /api/notifications/created-by-me

Student read state:

PATCH /api/notifications/{id}/read

Authorization must determine which notifications a student can see.

==================================================
33. NOTIFICATION READ STATE
===========================

If read/unread state is implemented per student, use a proper relationship.

Conceptually:

notification_reads

* notification_id
* student_id
* read_at

Do not store one global `read` field on the notification if different students can independently read it.

==================================================
34. ANALYTICS
=============

Analytics should be derived from authoritative database data.

Do not permanently store every dashboard statistic unless required.

Examples:

Overall attendance
Department attendance
Subject attendance
Low-attendance students
Gate-pass counts
Student counts

Create service-level analytics calculations.

Endpoints:

GET /api/analytics/overview

GET /api/analytics/attendance

GET /api/analytics/attendance/departments

GET /api/analytics/attendance/subjects

GET /api/analytics/gatepasses

==================================================
35. ROLE-SCOPED ANALYTICS
=========================

Admin:

Institution-wide analytics.

HOD:

Department-level analytics.

Faculty:

Only permitted attendance/session information.

Student:

Only personal information.

Never allow a frontend query parameter to bypass these restrictions.

For example:

GET /api/analytics?department=ECE

must NOT allow an HOD of CSE to retrieve ECE data simply by changing the parameter.

Authorization must be applied server-side.

==================================================
36. REPORTS
===========

Provide backend support for reports.

Potential endpoints:

GET /api/reports/attendance
GET /api/reports/students
GET /api/reports/gatepasses

Support filters such as:

* Date range
* Department
* Semester
* Section
* Subject

Do not duplicate report-generation logic in multiple routes.

Create a report service.

==================================================
37. API DESIGN
==============

Use consistent endpoint naming.

Recommended prefix:

/api

Authentication:

POST /api/auth/login
GET /api/auth/me

Students:

GET /api/students
GET /api/students/{id}
GET /api/students/me

Faculty:

GET /api/faculty/me

HOD:

GET /api/hod/me

Attendance:

POST /api/attendance/sessions
GET /api/attendance/sessions/my
GET /api/attendance/sessions/{id}
POST /api/attendance/sessions/{id}/submit
GET /api/attendance
GET /api/students/me/attendance

Gate Pass:

POST /api/gatepasses
GET /api/gatepasses/my
GET /api/gatepasses/{id}
GET /api/gatepasses/pending
PATCH /api/gatepasses/{id}/approve
PATCH /api/gatepasses/{id}/reject

Notifications:

GET /api/notifications
POST /api/notifications
GET /api/notifications/admin
PATCH /api/notifications/{id}/read

Analytics:

GET /api/analytics/overview
GET /api/analytics/attendance
GET /api/analytics/gatepasses

Reports:

GET /api/reports/attendance
GET /api/reports/students
GET /api/reports/gatepasses

==================================================
38. API RESPONSE FORMAT
=======================

Use consistent response structures.

Successful resource:

{
"data": {...}
}

Collection:

{
"data": [...],
"pagination": {
"page": 1,
"page_size": 20,
"total": 100
}
}

Errors should use appropriate HTTP status codes and structured messages.

Example:

{
"detail": "Gate pass has already been reviewed."
}

Do not expose internal stack traces.

==================================================
39. HTTP STATUS CODES
=====================

Use appropriate status codes.

Examples:

200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error

Do not return 200 for every failure.

==================================================
40. PAGINATION
==============

Large resources must support pagination.

Especially:

* Students
* Attendance
* Gate passes
* Notifications
* Reports

Use query parameters such as:

?page=1&page_size=20

Validate reasonable limits.

Do not allow clients to request millions of records in a single response.

==================================================
41. FILTERING
=============

Support server-side filtering where appropriate.

Examples:

GET /api/students?department=CSE&semester=6

GET /api/attendance?department=CSE&date=2026-09-28

GET /api/gatepasses?status=PENDING

GET /api/notifications?unread=true

Validate all filter parameters.

Do not construct raw SQL from user-provided strings.

==================================================
42. DATABASE TRANSACTIONS
=========================

Use database transactions for multi-step operations.

Especially:

Gate-pass approval:

Update status
+
Set HOD
+
Set review timestamp

Attendance submission:

Validate session
+
Validate records
+
Finalize session
+
Persist submission state

If one operation fails, the transaction should not leave partially updated data.

==================================================
43. DATABASE CONSTRAINTS
========================

Use database-level constraints wherever appropriate.

Examples:

* Unique username
* Unique student ID
* Unique faculty ID
* Unique roll number where appropriate
* Unique attendance record per student/session
* Valid foreign keys
* Non-null required fields

Do not rely entirely on application-level validation.

==================================================
44. ALEMBIC
===========

Use Alembic for database migrations.

Initial migration should create all required tables.

The project should support:

alembic upgrade head

and development rollback where appropriate.

Do not manually edit the production database schema.

==================================================
45. CONFIGURATION
=================

Use environment variables.

Example:

DATABASE_URL=postgresql+psycopg://...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development

Do not commit `.env`.

Provide:

.env.example

==================================================
46. DATABASE CONNECTION
=======================

Use SQLAlchemy session management.

Implement:

* Engine
* Session factory
* Dependency injection
* Proper session closing
* Transaction handling

Do not create a new unmanaged database connection for every individual operation.

==================================================
47. PYDANTIC SCHEMAS
====================

Separate database models from API schemas.

For example:

models/
student.py

schemas/
student.py

Do not expose SQLAlchemy models directly as your public API contract.

Create schemas such as:

StudentCreate
StudentUpdate
StudentResponse

GatePassCreate
GatePassResponse
GatePassReject

AttendanceSessionCreate
AttendanceSessionResponse

NotificationCreate
NotificationResponse

==================================================
48. PROJECT STRUCTURE
=====================

Use a modular structure similar to:

backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── base.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── hod.py
│   │   ├── admin.py
│   │   ├── department.py
│   │   ├── subject.py
│   │   ├── academic_class.py
│   │   ├── attendance.py
│   │   ├── gatepass.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── attendance.py
│   │   ├── gatepass.py
│   │   ├── notification.py
│   │   ├── analytics.py
│   │   └── reports.py
│   │
│   ├── api/
│   │   ├── router.py
│   │   │
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── students.py
│   │       ├── faculty.py
│   │       ├── hod.py
│   │       ├── admin.py
│   │       ├── attendance.py
│   │       ├── gatepass.py
│   │       ├── notifications.py
│   │       ├── analytics.py
│   │       └── reports.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── student_service.py
│   │   ├── attendance_service.py
│   │   ├── gatepass_service.py
│   │   ├── notification_service.py
│   │   ├── analytics_service.py
│   │   └── report_service.py
│   │
│   ├── repositories/
│   │   ├── student_repository.py
│   │   ├── attendance_repository.py
│   │   ├── gatepass_repository.py
│   │   └── notification_repository.py
│   │
│   └── utils/
│       └── ...
│
├── alembic/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
│
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md

You may adjust the structure if a technically superior organization is justified.

Do not create unnecessary abstraction layers merely for appearance.

==================================================
49. AUDIT LOGGING
=================

Implement an audit-log system for important actions.

Examples:

* Login
* Gate-pass approval
* Gate-pass rejection
* Attendance submission
* Notification publication
* Administrative changes

Conceptual:

audit_logs

* id
* user_id
* action
* resource_type
* resource_id
* timestamp
* metadata

Do not store passwords or sensitive secrets in audit logs.

Example:

HOD approved gate pass:

{
"action": "GATEPASS_APPROVED",
"resource_type": "gate_pass",
"resource_id": "...",
"user_id": "...",
"timestamp": "..."
}

==================================================
50. ERROR HANDLING
==================

Implement centralized exception handling where appropriate.

Handle:

* Validation errors
* Authentication failures
* Authorization failures
* Resource not found
* Duplicate resource conflicts
* Database failures
* Unexpected errors

Never expose internal database errors directly to clients.

Log technical details server-side.

Return safe client-facing messages.

==================================================
51. LOGGING
===========

Implement structured application logging.

Log important events such as:

* Startup
* Shutdown
* Authentication attempts
* API requests where appropriate
* Important business operations
* Exceptions
* Database failures

Do not log:

* Passwords
* JWT secrets
* Database credentials
* Sensitive personal information unnecessarily

==================================================
52. CORS
========

Configure CORS for the Student Web Application.

During development, allow the development frontend origin.

Do not use unrestricted production CORS such as:

allow_origins=["*"]

unless there is a documented reason.

Make allowed origins configurable.

==================================================
53. SECURITY REQUIREMENTS
=========================

Implement at minimum:

* Password hashing
* JWT authentication
* RBAC
* Input validation
* Parameterized ORM queries
* CORS configuration
* Secure configuration
* Appropriate HTTP status codes
* Authorization checks
* Database constraints

Do not assume that frontend validation provides security.

All important validation must occur on the backend.

==================================================
54. DATA OWNERSHIP
==================

This is critical.

Student:

Can access only their own private data.

Faculty:

Can access only authorized attendance sessions/data.

HOD:

Can access data belonging to their department unless broader permission is explicitly granted.

Admin:

Can access institution-wide information according to the authorization model.

Every endpoint returning private data must enforce this.

==================================================
55. SEED DATA
=============

Create a development seed mechanism.

Include sample:

* Departments
* Subjects
* Academic classes
* Students
* Faculty
* HOD
* Admin
* Attendance
* Gate passes
* Notifications

Use clearly documented development credentials.

Never use these credentials in production.

Provide a command or script such as:

python -m app.seed

or equivalent.

==================================================
56. API DOCUMENTATION
=====================

FastAPI should automatically expose:

/docs

/redoc

Ensure endpoints have:

* Meaningful descriptions
* Request schemas
* Response schemas
* Authentication requirements
* Appropriate response codes

Group routes by domain.

==================================================
57. TESTING
===========

Testing is mandatory.

Create tests for:

Authentication
Authorization
Students
Attendance
Gate passes
Notifications
Analytics

At minimum test:

### Authentication

* Valid login
* Invalid password
* Unknown user
* Inactive user

### Authorization

* Student cannot access Admin endpoint
* Student cannot approve gate pass
* Faculty cannot approve gate pass
* HOD cannot access another department's restricted data
* Admin can access permitted system-level endpoints

### Gate Pass

* Student creates request
* Invalid request rejected
* HOD approves
* HOD rejects
* Rejection requires reason
* Already-reviewed request cannot be reviewed again

### Attendance

* Faculty creates session
* Faculty can submit own session
* Faculty cannot submit another faculty's session
* Duplicate attendance rejected
* Student can retrieve own attendance
* Student cannot retrieve another student's attendance

### Notifications

* Admin can publish
* Authorized HOD can publish
* Student cannot publish
* Student can retrieve relevant notifications

==================================================
58. INTEGRATION TESTING
=======================

Test complete workflows.

Example:

STUDENT GATE PASS:

Student Login
↓
Create Gate Pass
↓
Database
↓
HOD Login
↓
View Pending Request
↓
Approve
↓
Database
↓
Student Retrieves Status
↓
APPROVED

Attendance:

Faculty Login
↓
Create Session
↓
Submit Attendance
↓
Database
↓
Student Requests Attendance
↓
Attendance Returned

Notification:

Admin Login
↓
Publish Notification
↓
Database
↓
Student Requests Notifications
↓
Notification Returned

==================================================
59. CLIENT INTEGRATION
======================

The backend must be designed around the APIs required by the four previously developed nodes.

Student Node requires:

* Login
* Profile
* Notifications
* Attendance
* Gate Pass

Admin Node requires:

* Dashboard
* Students
* Attendance
* Notifications
* Gate Pass monitoring
* Analytics
* Reports

Faculty Node requires:

* Login
* Faculty profile
* Subjects/classes
* Attendance sessions
* Attendance submission
* Attendance history
* Reports

HOD Node requires:

* Dashboard
* Gate-pass management
* Notifications
* Department attendance
* Department analytics
* Reports

==================================================
60. API CONTRACT CONSISTENCY
============================

Before implementation is considered complete:

Compare the backend API contracts against the previously defined client expectations.

Identify:

* Endpoint mismatches
* Request-field mismatches
* Response-field mismatches
* Authentication differences
* Role-permission differences

The backend should provide stable schemas that the clients can consume.

If a client-side API assumption is technically incorrect, document the correction rather than silently creating inconsistent behavior.

==================================================
61. DO NOT BUILD MICROservices
==============================

This project should use one backend application.

Do NOT create:

Authentication microservice
Attendance microservice
Notification microservice
Gate-pass microservice

unless there is a future architectural requirement.

Use a modular monolith:

FastAPI
├── Auth module
├── Student module
├── Attendance module
├── Gate Pass module
├── Notification module
├── Analytics module
└── Reports module

This is easier to develop, test, deploy, and maintain for the current project.

==================================================
62. DEVELOPMENT ORDER
=====================

Develop the backend in this order:

PHASE 1

Project setup
↓
Configuration
↓
Database connection
↓
SQLAlchemy models
↓
Alembic

PHASE 2

User model
↓
Password hashing
↓
Authentication
↓
JWT
↓
RBAC

PHASE 3

Students
↓
Faculty
↓
HOD
↓
Admin
↓
Departments
↓
Subjects
↓
Academic classes

PHASE 4

Attendance sessions
↓
Attendance records
↓
Attendance submission
↓
Attendance retrieval
↓
Attendance calculations

PHASE 5

Gate-pass workflow

PHASE 6

Notifications

PHASE 7

Analytics

PHASE 8

Reports

PHASE 9

Audit logs
↓
Logging
↓
Error handling

PHASE 10

Testing

PHASE 11

Client integration

==================================================
63. API INTEGRATION TESTING WITH THE CLIENTS
============================================

After the backend is stable:

Connect each node one at a time.

Order:

1. Student Web
2. HOD Desktop
3. Faculty Desktop
4. Admin Desktop

For each node:

Mock Service
↓
Replace with API Service
↓
Test authentication
↓
Test data retrieval
↓
Test mutations
↓
Test authorization
↓
Test error handling

Do not connect all four clients simultaneously before validating individual integrations.

==================================================
64. BACKEND DEVELOPMENT ENVIRONMENT
===================================

Provide clear setup instructions.

Expected setup:

Python virtual environment
↓
Install dependencies
↓
Create PostgreSQL database
↓
Configure .env
↓
Run Alembic migrations
↓
Seed development data
↓
Start FastAPI
↓
Open /docs

Example development command:

uvicorn app.main:app --reload

Use an appropriate project-specific command if the final structure differs.

==================================================
65. DOCKER
==========

Do not make Docker mandatory for the first development stage.

However, prepare the project so it can later be containerized.

Optionally provide:

Dockerfile
docker-compose.yml

for:

FastAPI
PostgreSQL

If Docker is included, do not unnecessarily containerize the four client applications during this stage.

==================================================
66. PERFORMANCE
===============

Avoid obvious performance problems.

Use:

* Database indexes
* Pagination
* Appropriate joins
* Efficient queries
* Selective response fields
* Proper relationship loading

Potential indexes:

users.username
students.student_id
students.department_id
attendance_sessions.date
attendance_records.student_id
attendance_records.session_id
gate_passes.status
gate_passes.student_id
notifications.created_at

Do not optimize prematurely, but do not create obviously inefficient queries.

==================================================
67. DATA INTEGRITY
==================

The backend is the authoritative source of truth.

Therefore:

Client data is untrusted.

All incoming data must be:

Validate
↓
Authorize
↓
Process
↓
Persist

Never trust:

* Client role
* Client user ID
* Client approval status
* Client attendance percentage
* Client timestamps
* Client ownership claims

The backend should derive authoritative values where possible.

==================================================
68. IMPORTANT BUSINESS RULES
============================

Implement these rules centrally.

Gate pass:

PENDING
→ APPROVED / REJECTED

Only authorized HOD can perform the transition.

Attendance:

A student cannot have multiple attendance records for the same session.

Only authorized faculty can finalize their session.

Student:

Can retrieve only their own private attendance and gate-pass information.

HOD:

Department scope must be enforced.

Admin:

Institution-level access according to defined permissions.

Notifications:

Students should receive only notifications applicable to them.

==================================================
69. FINAL ACCEPTANCE CRITERIA
=============================

The backend is considered Stage 1 complete when:

1. FastAPI starts successfully.
2. PostgreSQL connection works.
3. Alembic migrations work.
4. Seed data can be loaded.
5. Authentication works.
6. JWT authentication works.
7. Passwords are securely hashed.
8. RBAC works.
9. Student APIs work.
10. Faculty APIs work.
11. HOD APIs work.
12. Admin APIs work.
13. Attendance APIs work.
14. Gate-pass workflow works.
15. Notification system works.
16. Analytics endpoints work.
17. Report endpoints work.
18. Audit logging works.
19. Validation works.
20. Authorization is enforced server-side.
21. Pagination works where required.
22. Filtering works where required.
23. Database constraints are implemented.
24. Transactions are used for critical workflows.
25. Errors are handled consistently.
26. API documentation is available.
27. Unit tests pass.
28. Integration tests pass.
29. Development seed data works.
30. All four client nodes have clearly defined API integration points.

==================================================
70. FINAL DELIVERABLE
=====================

After implementation, provide a complete technical report containing:

1. Final backend architecture.
2. Complete project structure.
3. Database ER/data model explanation.
4. List of database tables.
5. Relationships between tables.
6. Authentication architecture.
7. Authorization/RBAC architecture.
8. Complete API endpoint catalog.
9. Request/response examples for important endpoints.
10. Attendance workflow.
11. Gate-pass workflow.
12. Notification workflow.
13. Analytics architecture.
14. Report architecture.
15. Audit logging architecture.
16. Error-handling strategy.
17. Testing strategy.
18. Seed-data strategy.
19. Environment setup instructions.
20. Migration instructions.
21. Server startup instructions.
22. API documentation location.
23. Client integration instructions.
24. Known limitations.
25. Future improvements.

==================================================
FINAL ARCHITECTURAL PRINCIPLE
=============================

The four client applications are presentation clients.

The FastAPI backend is the application authority.

PostgreSQL is the persistent source of truth.

The correct architecture is:

CLIENT
↓
AUTHENTICATED API REQUEST
↓
AUTHORIZATION
↓
VALIDATION
↓
BUSINESS LOGIC
↓
DATABASE
↓
RESPONSE
↓
CLIENT

Never bypass this architecture.

The backend must not become merely a collection of CRUD endpoints.

It must enforce the actual rules of the Smart Campus Management System.

The goal is to produce a maintainable, secure, testable central backend that can serve all four existing nodes without requiring major changes to their user interfaces.

Build the backend as a modular monolith first.

Keep domain boundaries clear.

Keep the API contract explicit.

Keep the database authoritative.

Keep authorization server-side.

Keep the four clients independent of the database.

The final system should be capable of evolving from a college project into a properly structured multi-client software system.

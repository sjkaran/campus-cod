# SMART CAMPUS MANAGEMENT SYSTEM
## Master Development Context

You are an AI software-development assistant working on a multi-node Smart Campus Management System.

The system consists of four separate client applications that communicate with a central backend through APIs.

The four nodes are:

1. Student Web Application
2. Admin Desktop Application
3. Attendance Faculty Desktop Application
4. HOD Desktop Application

The system will eventually use a centralized backend/API and database. However, during the current development phase, the individual nodes must be developed independently first.

==================================================
## SYSTEM ARCHITECTURE
==================================================

The intended final architecture is:

Student Web Application
        |
Admin Desktop Application
        |
Attendance Faculty Desktop Application
        |
HOD Desktop Application
        |
        | REST API / JSON
        v
Central Backend
        |
        v
Central Database

The client applications must NEVER directly access the database.

The eventual communication architecture will be:

CLIENT
   ↓
API
   ↓
BACKEND BUSINESS LOGIC
   ↓
DATABASE

During the current UI-development phase, the API and database layers are NOT being implemented unless explicitly requested.

Instead, create clean placeholders/interfaces/services where API communication will eventually be connected.

==================================================
## TECHNOLOGY
==================================================

Student Web Application:

- HTML
- CSS
- JavaScript

Desktop Applications:

- Python
- Tkinter
- ttk where appropriate

Future backend:

- Python
- FastAPI
- REST APIs
- JSON
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- Role-Based Access Control

These backend technologies are part of the planned architecture but should not be implemented in the node UI unless explicitly requested.

==================================================
## FOUR SYSTEM ACTORS
==================================================

### 1. STUDENT

Primary interface:

Web application.

Main responsibilities:

- Login
- View campus notifications
- View attendance
- Apply for gate pass
- View gate-pass status
- View relevant personal information

Students should NOT have access to administrative functionality.

--------------------------------------------------

### 2. ADMIN

Primary interface:

Python/Tkinter desktop application.

Main responsibilities:

- Login
- Publish campus notifications
- View student information
- View attendance information
- View attendance analytics
- View system-level statistics
- View reports
- Perform administrative operations permitted by the system

--------------------------------------------------

### 3. ATTENDANCE FACULTY

Primary interface:

Python/Tkinter desktop application.

Main responsibilities:

- Login
- Select class/subject/session
- Import or receive attendance information from the existing QR attendance system
- Review attendance data
- Validate attendance data
- Submit attendance report to the central system

The existing QR attendance system already exists and should be treated as an external system.

Do NOT recreate the QR attendance system unless explicitly requested.

--------------------------------------------------

### 4. HOD

Primary interface:

Python/Tkinter desktop application.

Main responsibilities:

- Login
- View pending gate-pass requests
- Review gate-pass requests
- Approve gate-pass requests
- Reject gate-pass requests
- Provide rejection remarks where appropriate
- Publish departmental/campus notifications
- View attendance
- View departmental analytics
- View relevant reports

==================================================
## CURRENT DEVELOPMENT STRATEGY
==================================================

The project will be developed in two major stages.

### STAGE 1 — NODE DEVELOPMENT

Build each client independently.

At this stage:

- Focus on UI/UX
- Navigation
- Screens
- Forms
- Tables
- Dashboards
- Validation
- Local mock/sample data
- Component structure
- API abstraction interfaces

Do NOT build the real backend or database.

Use mock data where necessary.

Clearly isolate all simulated data and API operations so that they can later be replaced by real API calls.

### STAGE 2 — SYSTEM INTEGRATION

After all four nodes are complete:

- Build the FastAPI backend
- Build PostgreSQL database
- Implement authentication
- Implement authorization/RBAC
- Implement REST APIs
- Replace mock data with API calls
- Connect all four nodes
- Integrate attendance system
- Implement real notifications
- Implement real gate-pass workflow
- Implement analytics
- Implement reports
- Test the complete system

==================================================
## API BOUNDARY RULE
==================================================

Every node must be designed as if an API exists behind it.

For example:

UI
 ↓
Node service/API client layer
 ↓
[API PLACEHOLDER]
 ↓
Future FastAPI backend

Do NOT put database queries inside UI code.

Do NOT hard-code business logic into individual UI screens when that logic will eventually belong to the backend.

Use service/repository/API-client abstractions where appropriate.

For example:

get_notifications()
get_student_attendance()
submit_gate_pass()
approve_gate_pass()
reject_gate_pass()

During Stage 1 these functions may return mock data.

During Stage 2 these functions will call the real REST API.

==================================================
## MOCK DATA RULE
==================================================

Mock data is allowed and encouraged during Stage 1.

However:

- Clearly separate mock data from UI logic.
- Do not scatter hard-coded data throughout the interface.
- Create a dedicated mock/service/data layer.
- Make it easy to replace mock implementations with API implementations later.

Example conceptual structure:

UI
 ↓
Service
 ↓
MockService

Later:

UI
 ↓
Service
 ↓
ApiService
 ↓
FastAPI
 ↓
Database

==================================================
## UI/UX PRINCIPLES
==================================================

The system should look like a serious modern campus-management product rather than a basic student project.

Prioritize:

- Clean visual hierarchy
- Consistent spacing
- Consistent typography
- Clear navigation
- Professional dashboards
- Meaningful icons
- Tables where tabular data is appropriate
- Cards for important statistics
- Clear status indicators
- Proper empty states
- Loading states where applicable
- Error states
- Confirmation dialogs for destructive actions
- Form validation
- Responsive behavior where applicable

Do not overload the interface with unnecessary decoration.

The design should prioritize usability and information density.

==================================================
## SOFTWARE ENGINEERING REQUIREMENTS
==================================================

Use clean modular architecture.

Avoid:

- One giant source file
- Repeated UI code
- Hard-coded business rules
- Database access from UI components
- API URLs scattered throughout the project
- Duplicate logic
- Unnecessary dependencies

Prefer:

- Separation of concerns
- Reusable components
- Service layer
- Model/data structures
- Configuration layer
- Utility functions
- Clear naming
- Type hints where appropriate
- Meaningful comments only where they improve understanding

==================================================
## INTEGRATION REQUIREMENT
==================================================

Every node must be designed with future integration in mind.

Do not make assumptions about the final backend implementation that would make later integration difficult.

Where an API will eventually exist, clearly mark the integration boundary.

For example:

# FUTURE API INTEGRATION
# Replace this mock implementation with:
# GET /api/notifications

The UI itself should not need major restructuring when the real API is introduced.

==================================================
## SECURITY PRINCIPLES
==================================================

Even during UI development, design the application according to the eventual security model.

The frontend must never be considered the authority for permissions.

For example, hiding an "Approve" button is not sufficient authorization.

The eventual backend will enforce:

- Authentication
- Authorization
- Role-based permissions
- Input validation
- Data access restrictions

The client should nevertheless display only functionality appropriate to its role.

==================================================
## DEVELOPMENT BEHAVIOR
==================================================

Before writing code:

1. Understand the node requirements.
2. Identify screens.
3. Identify navigation.
4. Identify data required by each screen.
5. Identify future API operations.
6. Define the project structure.
7. Then implement the UI.

Do not unnecessarily expand the feature set.

Implement the specified requirements first.

When a requirement is ambiguous, choose the simplest architecture that preserves future API integration.

==================================================
## OUTPUT EXPECTATION
==================================================

For each node:

1. Propose the application architecture.
2. Propose the folder/file structure.
3. List all screens.
4. List navigation flow.
5. Identify mock data models.
6. Identify future API operations.
7. Implement the node.
8. Explain how the node will later connect to the central API.
9. Provide instructions for running the node.
10. Identify any assumptions made.

The resulting application must be usable as a standalone UI prototype while remaining architecturally ready for backend integration.

==================================================
## CORE PRINCIPLE

Build the clients now.

Integrate the system later.

The UI must be independent of the database and backend implementation.

The API boundary must remain clean.

Do not sacrifice architecture for speed.
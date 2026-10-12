# Smart Campus Management System

A centralized campus management platform designed to streamline student services, attendance tracking, administrative operations, and departmental communication through a unified system.

## Live Website

**Student Portal:** [Visit the Student Website](https://sjkaran.github.io/campus-cod/)

## Overview

The Smart Campus Management System connects students, administrators, attendance faculty, and Heads of Department (HODs) through dedicated applications backed by a central REST API. It aims to improve operational efficiency, data consistency, and communication across campus.

## Key Modules

- **Student Web Portal:** View attendance, receive notifications, submit gate-pass requests, and track request status.
- **Admin Desktop Application:** Manage student records, publish campus notifications, monitor attendance, and access analytics.
- **Attendance Faculty Application:** Conduct QR-based attendance, review records, and submit finalized attendance reports.
- **HOD Desktop Application:** Review gate-pass requests, publish departmental notifications, and monitor departmental attendance.
- **Central Backend:** Handle authentication, role-based access control, business logic, and centralized data management.

## Technology Stack

| Component | Technologies |
|---|---|
| Student Portal | HTML, CSS, JavaScript |
| Desktop Applications | Python, Tkinter |
| Backend API | Python, FastAPI |
| Database | PostgreSQL |
| ORM & Migrations | SQLAlchemy, Alembic |
| Authentication | JWT, password hashing |
| Communication | REST API, JSON |

## Architecture

The system follows a centralized client-server architecture. Each application communicates with the backend through authenticated REST API endpoints, while PostgreSQL provides centralized data storage.

```text
Student Web Portal ───────┐
Admin Desktop App ────────┤
Attendance Faculty App ───┼──> FastAPI Backend ──> PostgreSQL
HOD Desktop App ──────────┘
```

## Repository Structure

```text
campus-cod/
├── student-web/         # Student web portal
├── admin_desktop/       # Administration application
├── attendance_desktop/  # QR attendance application
├── hod_desktop/         # HOD application
├── backend/             # FastAPI backend and database logic
├── prompts_to_build/    # Development prompts and specifications
├── README.md
└── SETUP_GUIDE.md
```

## Getting Started

For installation instructions, environment configuration, database setup, and local development, refer to [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Project Goals

- Centralize campus operations across multiple applications.
- Improve attendance visibility and reporting.
- Digitize gate-pass approval workflows.
- Enable structured communication between students and campus authorities.
- Maintain secure, role-based access to institutional data.

## Author

**Karan**  
GitHub: [@sjkaran](https://github.com/sjkaran)

---

*Developed as a software engineering project focused on centralized campus automation and application integration.*
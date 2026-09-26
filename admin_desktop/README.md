# Smart Campus Management System — Admin Desktop Application (Stage 1)

A standalone, polished Tkinter prototype for the College Administrator role,
built with a clean service-layer architecture so mock data can be swapped
for real FastAPI calls later without touching the UI.

---

## 1. Project Structure

```
admin_desktop/
├── main.py                     # Entry point: window, login flow, sidebar shell, routing
├── requirements.txt
│
├── config/
│   └── settings.py              # Theme tokens, fonts, thresholds, mock credentials
│
├── models/                      # Plain dataclasses — the shared "shape" of data
│   ├── admin.py
│   ├── student.py
│   ├── attendance.py
│   ├── notification.py
│   ├── gatepass.py
│   └── analytics.py
│
├── services/                    # THE layer the UI talks to. Mock now, API later.
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
│   └── api_client.py            # Centralized future HTTP boundary (unused in Stage 1)
│
├── mock/                        # ALL fake data lives here, nowhere else
│   ├── students.py
│   ├── attendance.py
│   ├── notifications.py
│   ├── gatepasses.py
│   └── analytics.py
│
├── ui/
│   ├── theme.py                 # ttk style configuration (buttons, tables, inputs)
│   ├── components.py            # Reusable: KPICard, DataTable, FilterBar, badges,
│   │                             #   dialogs, state placeholders, BarChart/DonutChart
│   ├── sidebar.py                # Persistent left navigation
│   ├── login.py
│   ├── dashboard.py
│   ├── students.py               # List + detail drill-down
│   ├── attendance.py
│   ├── notifications.py          # Composer + history
│   ├── gatepasses.py             # List + read-only detail
│   ├── analytics.py
│   ├── reports.py
│   └── settings.py
│
└── utils/
    ├── validators.py
    ├── formatters.py
    └── helpers.py
```

**Architecture flow (Stage 1):**

```
Tkinter UI  →  Service Layer  →  Mock Data Layer
```

**Architecture flow (Stage 2, unchanged from the UI's point of view):**

```
Tkinter UI  →  Service Layer  →  api/api_client.py  →  FastAPI  →  PostgreSQL
```

No UI file imports anything from `mock/` directly. No UI file contains
business rules (thresholds, filtering logic, recipient counts) — those
live in `services/` and `config/settings.py`.

---

## 2. Installing & Running

```bash
# 1. Ensure Python 3.10+ with Tkinter is available
python3 --version

# (Linux only, if Tkinter isn't already installed)
sudo apt-get install python3-tk

# 2. No pip installs are required — pure standard library.

# 3. Run it
cd admin_desktop
python3 main.py
```

### Mock Admin credentials (Stage 1 only — not real authentication)

| Username       | Password     |
|----------------|--------------|
| `admin`        | `admin123`   |
| `campus.admin` | `campus@2026`|

---

## 3. Implemented Screens

1. **Login** — Admin ID/password form, show/hide password, empty-field &
   invalid-credential validation, simulated loading state.
2. **Dashboard** — KPI cards (Total Students, Average Attendance, Pending
   Gate Passes, Today's Presence, Notifications Published), recent
   notifications panel, recent gate-pass activity panel.
3. **Students** — Searchable/filterable directory (department, semester,
   section, status) → drill-down **Student Detail** view (personal info,
   academic overview with per-subject attendance, gate-pass summary,
   recent gate-pass activity).
4. **Attendance** — Institution-wide monitoring table with department /
   semester / section / subject / status filters, plus a summary strip
   (overall %, below-threshold count, critically-below count). No editing.
5. **Notifications** — Composition form (title, message, audience,
   audience detail, priority, expiration), Preview, publish confirmation
   dialog ("Publish this notification to N students?"), and a filterable
   notification history table.
6. **Gate Passes** — Monitoring table (department/status filters) → **read-only**
   detail view. No approve/reject controls anywhere (see Section 6).
7. **Analytics** — KPI strip + six chart panels (students by department,
   attendance by department, attendance by subject, students by semester,
   gate-pass status donut, notifications-by-audience donut), each answering
   a specific administrative question.
8. **Reports** — Report type + department/semester/section parameters,
   Generate → tabular preview, Export placeholder (Stage 2 integration
   point).
9. **Settings** — Admin profile, session info, application info, display
   preferences placeholder.

All data-driven screens implement **Loading / Success / Empty / Error**
states via `ui/components.py::StatePlaceholder`, and destructive/consequential
actions (publish notification, logout) use a confirmation dialog.

---

## 4. Implemented Workflows

- Login → Dashboard → navigate via persistent sidebar → Logout (with
  confirmation) → back to Login.
- Search/filter students → open a student's full detail record.
- Filter attendance by multiple dimensions; see live-updating summary.
- Compose → Preview → confirm → Publish a notification; it immediately
  appears at the top of Notification History.
- Filter/browse gate passes → open a request's full detail (view-only).
- Browse analytics dashboards with charts built from the same underlying
  mock dataset as the other screens (numbers stay consistent everywhere).
- Select report parameters → Generate → preview table → Export (mocked).

---

## 5. Mock-Data Architecture

All simulated data lives exclusively under `mock/`:

- `mock/students.py` — generates 240 realistic student records (Indian
  names, 5 departments, semesters 1–8, sections A–C, ~92% ACTIVE).
- `mock/attendance.py` — generates 2–3 subject attendance records per
  active student, using a skewed distribution so most students are
  healthy and a realistic minority fall below the warning/critical
  thresholds defined in `config/settings.py`.
- `mock/gatepasses.py` — generates ~160 gate-pass requests with
  PENDING/APPROVED/REJECTED status and department-appropriate HOD names.
- `mock/notifications.py` — a seeded, realistic notification history
  (ACTIVE/EXPIRED/DRAFT) plus `add_notification()` for the publish flow.
- `mock/analytics.py` — derives all analytics **from the other mock
  modules** rather than inventing separate numbers, so the Dashboard,
  Students, Attendance and Analytics screens never disagree with each
  other.

Data is cached at module level per run (like an in-memory table), so
filtering/searching/publishing behaves consistently within a session,
the way a real backend-backed app would.

**No mock data is imported directly by any `ui/` file.** UI → Services →
Mock is the only permitted path.

---

## 6. Role Separation — Admin vs. HOD

The Admin and HOD are modeled as **distinct roles** per the specification:

| Capability                        | Admin | HOD |
|-----------------------------------|:-----:|:---:|
| View gate-pass requests           | ✅    | ✅  |
| **Approve / reject gate passes**  | ❌    | ✅  |
| View attendance                   | ✅ (monitor) | ✅ |
| **Submit attendance**             | ❌ (Faculty) | ❌ |
| Publish notifications             | ✅ (campus-wide) | ✅ (departmental) |
| System-wide analytics             | ✅    | ❌ (dept-level only) |

Concretely, `ui/gatepasses.py` renders **no** approve/reject buttons or
menu actions anywhere — not even hidden/disabled ones — and the detail
view explicitly states the record is read-only for Admin. This is a
UI-level convenience only: **the eventual FastAPI backend must
independently re-verify Admin-vs-HOD authorization on every request**,
since the frontend is never the authorization boundary (see Section 8).

---

## 7. Service Layer

Every screen calls a function like `get_students(...)`, `get_attendance(...)`,
`publish_notification(...)`, etc. — never a mock module and never a raw
data structure. Today:

```
UI → services.student_service.get_students(...) → mock.students.get_all_students()
```

Tomorrow (Stage 2), only the *inside* of each service function changes:

```
UI → services.student_service.get_students(...) → api.api_client.get("/api/students", ...)
```

The function signatures, return types (`Student`, `AttendanceRecord`, …
dataclasses), and calling convention stay identical — so no UI screen
needs to be rewritten.

---

## 8. API Integration Boundary

`api/api_client.py` defines the single centralized `ApiClient` class that
Stage 2 will implement with `requests`/`httpx`. It currently raises
`NotImplementedError` on every method — intentionally: it exists purely
to mark the boundary and give the service layer something concrete to
call into later. No API URLs appear anywhere outside this file.

Planned base URL / auth handling: `config/settings.py::API_BASE_URL`,
token attachment via `ApiClient.set_auth_token()`.

**Security note:** the frontend must never be treated as an authorization
boundary. Hiding the "Approve" button from Admin (Section 6) is a UX
convenience, not a security control — the backend must enforce RBAC
independently once implemented.

---

## 9. Future API Endpoints (conceptual contract)

```
POST   /api/auth/login

GET    /api/admin/dashboard

GET    /api/students
GET    /api/students/{id}
GET    /api/students/{id}/attendance
GET    /api/students/{id}/gatepasses

GET    /api/attendance
GET    /api/attendance/summary
GET    /api/attendance/students/{id}

GET    /api/notifications/admin
POST   /api/notifications

GET    /api/gatepasses
GET    /api/gatepasses/{id}

GET    /api/analytics/overview
GET    /api/analytics/attendance
GET    /api/analytics/attendance/departments
GET    /api/analytics/attendance/subjects
GET    /api/analytics/gatepasses

GET    /api/reports/students
GET    /api/reports/attendance
GET    /api/reports/gatepasses
```

Each service module has a docstring noting exactly which endpoint(s) it
will call in Stage 2.

---

## 10. Known Limitations (Stage 1)

- All data resets on application restart (in-memory only, no persistence).
- Authentication is a hard-coded credential check — not secure, not for
  production use, and has no session expiry.
- "Export" in Reports shows a confirmation of intent rather than writing
  a real CSV/PDF file (kept intentionally out of scope per the master
  prompt: "do not build complex backend report-generation infrastructure").
- Pagination is simulated by filtering an in-memory list rather than true
  server-side paging; with ~240 students / ~540 attendance rows this
  remains responsive, but very large datasets would need real pagination
  once the backend exists.
- Charts are custom `tkinter.Canvas` drawings (no external charting
  library) to avoid an unnecessary dependency for Stage 1 — sufficient for
  bar/donut visualizations at this scale.

## 11. Assumptions Made

- Attendance thresholds (75% warning / 65% critical) are treated as
  Stage 1 mock configuration in `config/settings.py`, per the spec's note
  that they must eventually be backend-configurable.
- "Notifications Published" KPI counts all notifications ever published
  (not just currently active) — a reasonable admin-facing lifetime metric.
- Gate-pass "Reviewing Authority" is derived from the student's department
  (one HOD per department) since the HOD node/roster wasn't specified here.
- Draft notifications are a UI-only prototype concept, as explicitly
  permitted by the spec, and are not distinguished by any special workflow
  beyond appearing with a DRAFT status badge in history.
- Report "Export" is mocked as a confirmation dialog rather than a file
  write, consistent with "Stage 1 report generation may use mock data" and
  the instruction not to build report-generation infrastructure yet.

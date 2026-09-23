# HOD Desktop Application — Stage 1 Prototype

Part of the Smart Campus Management System. This is the standalone
HOD (Head of Department) node: a Python/Tkinter desktop app built
against a mock data layer, architected so the mock layer can be
swapped for the real FastAPI backend in Stage 2 with no UI changes.

## 1. How to run it

Requirements: Python 3.10+ with Tkinter (bundled with most standard
Python installs; on Debian/Ubuntu install it with `sudo apt-get install
python3-tk` if `import tkinter` fails).

```
cd hod_desktop
python main.py
```

Demo login credentials:

- HOD ID: `HOD001`
- Password: `hod123`

No other dependencies are required — everything (including the
analytics charts) is built with the standard library.

## 2. Project structure

```
hod_desktop/
├── main.py                  # Entry point — creates the window, shows login then the app shell
├── config/
│   └── settings.py          # Colors, fonts, sizes, nav items, thresholds, DATA_SOURCE_MODE flag
├── models/                  # Plain dataclasses mirroring the future API response shapes
│   ├── student.py
│   ├── gatepass.py
│   ├── notification.py
│   └── attendance.py
├── services/                 # THE API BOUNDARY — UI code only ever calls these
│   ├── auth_service.py
│   ├── gatepass_service.py
│   ├── notification_service.py
│   ├── attendance_service.py
│   ├── analytics_service.py
│   ├── dashboard_service.py  # aggregates the above for the dashboard screen
│   └── reports_service.py
├── mock/
│   └── mock_data.py          # All sample data + in-session "persistence" (approve/reject/publish)
├── api/
│   └── api_client.py         # Stage-2 HTTP client stub — one method per future endpoint
├── ui/
│   ├── theme.py               # Centralized ttk styling (colors/fonts/button variants)
│   ├── widgets.py              # Reusable Card, StatCard, StatusBadge, EmptyState, table builder, dialogs
│   ├── app.py                   # App shell: header, sidebar nav, content-area screen switcher
│   ├── login.py                  # Screen 1
│   ├── dashboard.py                # Screen 2
│   ├── gatepass.py                  # Screen 3 (list + detail sub-views, approve/reject dialogs)
│   ├── notifications.py              # Screen 4
│   ├── attendance.py                  # Screen 5
│   ├── analytics.py                    # Screen 6 (canvas-based bar/segment charts, no extra deps)
│   ├── reports.py                       # Screen 7
│   └── settings.py                       # Session/profile info screen
└── utils/
    └── helpers.py             # attendance_band(), date validation, misc formatting
```

## 3. Screens implemented

1. **Login** — HOD ID/password, show/hide password toggle, inline
   error on bad credentials. Auth is routed through
   `services/auth_service.py`, which is the only place Stage 2's real
   `POST /api/auth/login` call needs to be added.
2. **Dashboard** — four stat cards (Pending Passes, Today's Passes,
   Department Attendance, Students Below Threshold — each clickable,
   jumping to the relevant screen), a recent-activity feed built from
   recent gate-pass decisions, and a recent-notifications panel.
3. **Gate Pass Management** — the core feature. A filterable table
   (Pending / All Requests) with all the columns from the spec, a
   detail view with full student/gate-pass info and prior-pass
   history, and Approve (confirmation dialog) / Reject (modal
   requiring a non-empty reason) actions.
4. **Notifications** — a publish form (title, message, audience,
   priority, expiration date) with validation, and a history table of
   previously published notifications with computed PUBLISHED/EXPIRED
   status.
5. **Attendance** — filterable by semester, section, and subject
   (department is implicit to this HOD), with a color-coded
   Good/Normal/Attention legend and status column. Thresholds are UI
   presentation rules only, per the spec.
6. **Analytics** — average attendance, distribution across
   Good/Normal/Attention bands, subject-wise and semester-wise bar
   charts, all drawn on plain `tk.Canvas` (no extra dependencies).
7. **Reports** — select a report type (Department Attendance, Student
   Attendance, Gate Pass, Notification) and generate a live preview
   from current mock data. No backend report storage, per spec.

Settings (session/profile info) and Logout are also implemented,
rounding out the sidebar from the spec's layout mock-up.

## 4. Mock data architecture

All sample data lives in `mock/mock_data.py`: one HOD account, ~90
generated students across 3 semesters/sections, ~26 gate-pass
requests in a realistic status mix, a handful of notifications, and a
full attendance matrix (student × subject). Nothing else in the
codebase hard-codes data — every screen goes through a `services/*`
function, which is what keeps the mock layer swappable.

`mock_data.py` also holds small "mutation" functions
(`approve_gatepass_record`, `reject_gatepass_record`,
`add_notification_record`) so that actions taken in the UI persist
for the running session, simulating what a real backend would do.

## 5. API integration points

Every service function has a `Future API:` comment naming the exact
endpoint it will call in Stage 2, e.g.:

```python
def get_pending_gatepasses():
    """Future API: GET /api/gatepasses/pending"""
    ...
```

`api/api_client.py` mirrors this as a class with one method per
endpoint (all currently `raise NotImplementedError`). The intended
Stage 2 change is:

1. Implement the HTTP calls in `ApiClient` (using `requests` or
   `httpx`, plus JWT attachment).
2. In each `services/*.py` file, branch on
   `config.settings.DATA_SOURCE_MODE` (or simply swap the import) to
   call `api_client` instead of `mock.mock_data`.
3. No changes needed in `ui/*.py` — every screen only imports from
   `services`, never from `mock` or `api` directly.

## 6. What changes when the FastAPI backend is introduced

- `services/*.py` bodies swap their mock-data calls for
  `ApiClient` calls; function signatures and return types (the
  `models/*.py` dataclasses) stay the same.
- `services/auth_service.login()` starts storing a real JWT and
  attaching it to `ApiClient`.
- Validation currently done client-side (e.g. non-empty rejection
  reason, non-empty notification fields) stays as a UX nicety, but
  the backend becomes the actual authority — exactly as required by
  the "frontend is never the authority for permissions" principle in
  the master spec.
- Loading states: Stage 1 mock calls are instant, so no spinners were
  needed. Stage 2 network calls should add a lightweight loading
  indicator around each `services/*` call site (the service layer
  boundary makes this a small, local change per screen).

## 7. Assumptions made

- The HOD account is scoped to a single department (Computer Science
  & Engineering in the mock data); every screen implicitly filters to
  "this HOD's department" rather than showing a department picker,
  since the spec describes the HOD as a departmental authority.
- "Today's Gate Passes" on the dashboard means passes with a
  departure date of today, across any status.
- Attendance analytics group only by subject and semester (as listed
  in the spec); section-level analytics were left out of the
  Analytics screen since Attendance already offers section filtering.
- Reports are generated as readable in-app text previews rather than
  exported files (PDF/CSV), since Stage 1 explicitly excludes backend
  report storage and no export format was specified.
- Expiration date entry uses a plain validated text field
  (`YYYY-MM-DD`) rather than a calendar-picker widget, to avoid adding
  a third-party dependency for a Stage 1 prototype.

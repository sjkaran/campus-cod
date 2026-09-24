# Smart Campus — Student Web Application (Stage 1 Prototype)

A standalone, front-end-only prototype of the Student node of the Smart
Campus Management System. Built with plain HTML/CSS/JavaScript (ES
modules, no framework, no build step) per the master and node prompts.

## 1. Architecture

```
Student UI (pages/, components/)
        ↓
Service layer (services/*.js)   <-- UI only ever calls this
        ↓
   Stage 1: mock/*.js (in-memory mock data)
   Stage 2: api/apiClient.js  →  FastAPI backend  →  PostgreSQL
```

- **`src/pages/`** — one module per screen (Login, Dashboard, Notifications,
  Attendance, Gate Pass, Gate Pass Details, Profile). Pages own their local
  state and call services; they never touch mock data directly.
- **`src/components/`** — reusable, stateless UI pieces (Sidebar, Navbar,
  StatCard, ProgressRing, NotificationCard, AttendanceTable, GatePassCard,
  StatusBadge, Modal, Toast, DataState loading/empty/error views).
- **`src/services/`** — the API abstraction boundary: `authService`,
  `studentService`, `notificationService`, `attendanceService`,
  `gatePassService`. Every function is written and commented as if it may
  call the network; each contains a `// FUTURE API INTEGRATION` comment
  showing the exact endpoint it will call in Stage 2.
- **`src/api/apiClient.js`** — placeholder HTTP client (fetch wrapper with
  auth-header injection) that is not used yet, but defines the shape
  services will call once Stage 2 begins.
- **`src/mock/`** — isolated mock data (students, notifications, attendance,
  gate passes) and a mutable in-memory gate-pass store so submissions
  persist for the session.
- **`src/models/models.js`** — JSDoc type shapes shared by mock data and
  (eventually) API responses, so the UI is never coupled to one or the
  other.
- **`src/utils/`** — validation, formatting, DOM helper (`h()`), icons, and
  app-wide constants (routes, statuses, mock attendance threshold).
- **`src/app.js`** — the app shell: a tiny hash-based router
  (`#/dashboard`, `#/notifications`, `#/attendance`, `#/gatepass`,
  `#/gatepass/GP001`, `#/profile`), auth guard, and sidebar/navbar/page
  composition.
- **`src/styles/`** — `variables.css` (design tokens), `global.css` (reset +
  shell layout), `components.css` (buttons/cards/tables/forms/modal/toast),
  `pages.css` (login screen).

No component ever reads from `mock/` directly, and no UI file contains a
database call, business rule about attendance thresholds, or gate-pass
approval logic — all of that is expected to live in the future backend.

## 2. Running the app

No dependencies to install — it's plain HTML/CSS/JS loaded as ES modules,
which requires serving over HTTP (not `file://`).

```bash
cd student-web

# option A — Node
npm start          # runs: npx http-server . -p 5173 -c-1

# option B — Python (no Node required)
npm run serve       # runs: python3 -m http.server 5173
```

Then open **http://localhost:5173**.

## 3. Mock credentials

```
Student ID: STU-2026-001
Password:   campus123
```

(Also shown on the login screen itself for convenience.)

## 4. Implemented screens

1. **Login** — branded split-screen layout, show/hide password, validation,
   loading state, error state, mock credential hint.
2. **Dashboard** — welcome message, attendance progress ring + summary,
   gate-pass status counts, 4 most recent notifications, quick actions.
3. **Notifications** — full list with search, filter (All / Unread / High
   priority), unread indicator, mark-as-read, empty/error/loading states.
4. **Attendance** — overall summary cards, subject-wise table with inline
   meters, below-threshold warning banner, filterable history table
   (subject, status, date range).
5. **Gate Pass** — apply form (destination, reason, departure/return
   date+time, remarks) with full validation, submit confirmation modal,
   success toast, and a history list of past requests with status badges
   and rejection reasons.
6. **Gate Pass Details** — full record, status timeline
   (Submitted → Under Review → Approved/Rejected), reviewer remarks.
7. **Profile** — read-only student information (ID, roll number, contact,
   department, semester, section, admission year).
8. **Logout** — confirmation modal, clears the mock session, returns to
   Login.

## 5. Student workflows implemented

- Log in / log out with mock session persisted in `sessionStorage`.
- Browse and filter campus notifications; mark individual notifications read.
- Review overall + subject-wise attendance and filtered attendance history.
- See an attendance warning when a subject falls below the mock threshold.
- Submit a gate-pass request (validated, confirmed, then appears instantly
  in history with `PENDING` status).
- Track gate-pass status and open full details, including rejection
  remarks, for any past request.
- View (read-only) profile information.

All administrative, faculty, and HOD functionality (approving passes,
submitting attendance, publishing notifications, analytics) is intentionally
**not present** in this node, per the role boundary in the prompts.

## 6. Mock-data architecture

`src/mock/` holds one file per entity (`students.js`, `notifications.js`,
`attendance.js`, `gatePasses.js`) with realistic sample records matching the
shapes in `models/models.js`. `gatePasses.js` also exposes a tiny in-memory
mutation (`generateGatePassId`) so new submissions persist for the browser
session — this is intentionally the *only* mutable mock module. Nothing in
`pages/` or `components/` imports from `mock/` directly; only `services/`
does.

## 7. API abstraction layer

Every screen goes through a service function:

```
loginStudent(username, password)
getCurrentStudent()
getNotifications() / markNotificationAsRead(id)
getAttendanceSummary() / getSubjectAttendance() / getAttendanceHistory(filters)
submitGatePass(data) / getMyGatePasses() / getGatePassDetails(id)
```

Each is `async`, simulates network latency, and contains a
`// FUTURE API INTEGRATION` comment showing the real call it will make once
`api/apiClient.js` is wired to the live backend. Swapping Stage 1 → Stage 2
means editing the *inside* of these functions only — no page or component
needs to change.

## 8. Future API endpoints required (Stage 2)

| Purpose | Endpoint |
|---|---|
| Login | `POST /api/auth/login` |
| Current student | `GET /api/students/me` |
| Notifications | `GET /api/notifications` |
| Mark notification read | `PATCH /api/notifications/{id}/read` |
| Attendance summary | `GET /api/students/me/attendance` |
| Subject-wise attendance | `GET /api/students/me/attendance/subjects` |
| Attendance history | `GET /api/students/me/attendance/history` |
| Submit gate pass | `POST /api/gatepasses` |
| My gate passes | `GET /api/gatepasses/my` |
| Gate pass details | `GET /api/gatepasses/{id}` |

## 9. Where Stage 2 integration happens

1. Implement `apiRequest()` calls properly in `src/api/apiClient.js`
   (base URL, JWT storage, error handling already scaffolded).
2. In each `src/services/*.js` file, replace the mock-data line with the
   commented `apiClient` call directly above it.
3. Delete `src/mock/` once no service references it.
4. No changes required in `src/pages/`, `src/components/`, or `src/app.js`.

## 10. Assumptions made

- A lightweight hash router (`#/route`) was used instead of a framework
  router, since only 6 screens are needed and the prompt asked to avoid
  unnecessary complexity/dependencies.
- The attendance warning threshold (75%) is treated as mock backend
  configuration (`utils/constants.js → APP_CONFIG`), not hard-coded per
  screen, so it can later be fetched from a config endpoint.
- Gate-pass "Under Review" is shown as an implicit step between Submitted
  and Approved/Rejected in the UI timeline only; the mock data model itself
  only stores `PENDING/APPROVED/REJECTED`, matching the future API contract.
- Profile is read-only in Stage 1, since editing wasn't required and the
  prompt says not to implement it unless explicitly requested.
- Notification "audience/category" filtering was implemented as a simple
  priority + read/unread + text search, since no specific category taxonomy
  was specified.

## 11. Known limitations

- No real authentication, authorization, or data persistence beyond the
  current browser session (`sessionStorage` for the session token,
  in-memory array for new gate passes — both reset on full reload of mock
  modules in a fresh tab).
- No pagination — mock data volumes are small enough that filtering client-
  side is sufficient for the prototype.
- No automated tests included (out of scope for a UI-only Stage 1 prompt).

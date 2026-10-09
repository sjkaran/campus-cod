# Smart Campus Management System — Setup & Integration Guide

This guide walks through getting the FastAPI backend running from zero, and then
wiring it up to the four existing client apps (Student web, Admin desktop,
Attendance Faculty desktop, HOD desktop) so the whole system works end to end.

Treat this as a checklist. Do the sections in order — each one depends on the last.

---

## 0. Before you start

- The backend was written and syntax-checked in an environment with **no internet
  access**, so it has never actually been installed or run. Expect to fix a small
  bug or two the first time you run it — this guide tells you how to find and fix
  them quickly (Section 5).
- Put the `backend/` folder at the root of the `campus-cod` repo, next to your
  existing client folders, e.g.:

```
campus-cod/
├── backend/              <- new, from this delivery
├── student-web/          <- existing
├── admin-desktop/        <- existing
├── faculty-desktop/      <- existing
└── hod-desktop/          <- existing
```

---

## 1. Install prerequisites

| Tool | Why | Check with |
|---|---|---|
| Python 3.11+ | Runs the backend | `python3 --version` |
| PostgreSQL 14+ | The database | `psql --version` |
| pip / venv | Python package management | comes with Python |

**Windows users:** install PostgreSQL from postgresql.org (the installer includes
`psql` and pgAdmin, a GUI you can use instead of the command line below).
**macOS:** `brew install postgresql@16 && brew services start postgresql@16`.
**Linux:** `sudo apt install postgresql postgresql-contrib`.

---

## 2. Create the database

Pick **one** of these:

**Command line:**
```bash
createdb smart_campus
```

**pgAdmin (GUI):** right-click *Databases* → *Create* → *Database…* → name it
`smart_campus`.

If `createdb` complains about a role/user, create one first:
```bash
sudo -u postgres createuser --superuser --pwprompt campus
sudo -u postgres createdb -O campus smart_campus
```

---

## 3. Set up the backend

```bash
cd campus-cod/backend

# 1. Virtual environment (keeps these packages separate from the rest of your system)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
```

Now open `.env` and edit two lines:

```bash
DATABASE_URL=postgresql+psycopg://campus:yourpassword@localhost:5432/smart_campus
JWT_SECRET_KEY=<paste a long random string here>
```

Generate a good secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Leave the rest of `.env` at its defaults for now (CORS origins already include
common local dev ports like `5500`, `3000`, `8080` — adjust once you know which
port your Student web app runs on, see Section 6).

```bash
# 4. Create the tables
alembic upgrade head

# 5. Load sample data (departments, students, faculty, a few gate passes and
#    notifications) so there's something to look at immediately
python -m app.seed
```

You'll see a list of development login credentials printed — also saved at the
top of `app/seed.py`:

```
admin      / Admin@12345
hod_cse    / Hod@12345
fac_cse1   / Faculty@12345
s2026001   / Student@12345
```

```bash
# 6. Run it
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** — this is an interactive page listing every
endpoint. Click **Authorize**, log in via `/api/auth/login` with one of the
credentials above to get a token, paste it in, and you can try any endpoint
directly from the browser.

---

## 4. Run the automated tests

Before connecting any clients, confirm the backend itself works:

```bash
pytest
```

This runs against a temporary in-memory database — it doesn't touch your real
PostgreSQL database or seed data, so it's safe to run any time.

- **All green?** Move to Section 6.
- **Some failures?** Go to Section 5.

---

## 5. If something breaks (expected, first run)

Since this code has never executed before, treat the first `pytest` run as a
debugging pass, not a sign something is fundamentally wrong. Common first-run
issues and fixes:

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError` | a package name/version mismatch in `requirements.txt` | check the error for the module name, `pip install <name>` |
| `ImportError` between `app/models/*.py` | a relationship or column reference typo | the traceback names the file and line — usually a one-line fix |
| Alembic errors on `upgrade head` | database not reachable, or `DATABASE_URL` malformed | re-check `.env`, confirm `psql smart_campus` connects |
| A specific test fails (not a crash) | a genuine logic bug | read the assertion message — it tells you what was expected vs. returned |
| Argon2 / psycopg build errors on `pip install` | missing system build tools | macOS: `xcode-select --install`; Linux: `sudo apt install build-essential libpq-dev` |

If you get stuck on a specific traceback, paste it back to me — with the actual
error in hand I can give you an exact fix rather than a guess.

---

## 6. Connect the four clients

The backend running on its own doesn't automatically talk to your existing
apps. Each client currently calls its own **mock service layer** (per your
original build spec — functions like `get_notifications()`,
`submit_gate_pass()` that return fake data). Making the system "fully
functioning" means replacing each of those mock functions with a real HTTP
call to this backend, one client at a time. The architecture was built so this
swap doesn't require touching any UI code — only the service layer.

### General pattern for every client

1. **Log in first.** Call `POST /api/auth/login` with `{"username", "password"}`.
   Store the returned `access_token` (in memory for desktop apps; in memory or
   `sessionStorage` for the web app — see the security note below).
2. **Send it on every other request** as a header:
   `Authorization: Bearer <access_token>`.
3. **Read responses consistently.** A single item comes back as
   `{"data": {...}}`. A list comes back as
   `{"data": [...], "pagination": {"page", "page_size", "total"}}`.
   Errors come back as `{"detail": "message"}` with a matching HTTP status
   code (401 not logged in, 403 not allowed, 404 not found, 409 conflict, 422
   bad input).
4. **If a token expires or is rejected (401),** send the user back to the
   login screen — don't try to silently retry.

### 6.1 Student Web Application (HTML/CSS/JS)

- Base URL during development: `http://localhost:8000/api`.
- Replace whatever mock module currently backs functions like
  `login()`, `getNotifications()`, `getMyAttendance()`, `applyGatePass()`,
  `getMyGatePasses()` with `fetch()` calls to:
  - `POST /auth/login`
  - `GET /notifications`
  - `GET /students/me/attendance`
  - `POST /gatepasses`
  - `GET /gatepasses/my`
- **CORS:** the backend only allows the origins listed in `.env`'s
  `CORS_ORIGINS`. Find out what port your web app is served from (e.g. Live
  Server on `5500`, or a plain `python -m http.server` on `8080`) and make
  sure that exact origin is in the list, then restart `uvicorn`.
- **Token storage:** for a browser app, keep the token in memory (a JS
  variable) if possible; if you need it to survive a page refresh,
  `sessionStorage` is a reasonable middle ground for this stage of the
  project. Avoid `localStorage` for anything longer-lived without adding
  refresh-token support later.

Example:
```js
async function login(username, password) {
  const res = await fetch("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  const data = await res.json();
  sessionStorage.setItem("token", data.access_token);
  return data.user;
}

async function getMyAttendance() {
  const res = await fetch("http://localhost:8000/api/students/me/attendance", {
    headers: { Authorization: `Bearer ${sessionStorage.getItem("token")}` },
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return (await res.json()).data;
}
```

### 6.2 Admin Desktop Application (Python/Tkinter)

- Use the `requests` library (`pip install requests` in that project's
  environment) inside the existing API-client/service layer — do **not** add
  HTTP calls into Tkinter widget code directly, per your architecture rules.
- Store the token in a module-level variable or a small session object created
  at login; pass it into your existing service classes.
- Key endpoints to wire up: `GET /students`, `GET /analytics/overview`,
  `GET /analytics/attendance`, `POST /notifications`,
  `GET /reports/students`, `GET /reports/attendance`,
  `GET /reports/gatepasses` (add `?format=csv` if the UI has an "export"
  button — it returns a downloadable CSV file instead of JSON).

```python
import requests

BASE_URL = "http://localhost:8000/api"

class ApiService:
    def __init__(self):
        self.token = None

    def login(self, username, password):
        r = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        r.raise_for_status()
        data = r.json()
        self.token = data["access_token"]
        return data["user"]

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_students(self, **params):
        r = requests.get(f"{BASE_URL}/students", headers=self._headers(), params=params)
        r.raise_for_status()
        return r.json()  # {"data": [...], "pagination": {...}}
```

### 6.3 Attendance Faculty Desktop Application (Python/Tkinter)

This one has the multi-step workflow — make sure the UI walks through it in
order, since the backend enforces the same order:

1. Faculty logs in.
2. `GET /faculty/me` to see which subjects/classes they're assigned to (use
   this to populate the "select class/subject" screen instead of hard-coding
   it).
3. `POST /attendance/sessions` to create a session for the chosen
   subject/class/date. Include `external_session_id` if the QR system gives
   you one — the backend uses it to prevent importing the same QR session
   twice.
4. `PATCH /attendance/sessions/{id}/status` with `{"status": "ACTIVE"}` when
   the session starts.
5. Import/receive the QR attendance data as your app already does (this
   backend does not talk to the QR system — that integration stays inside
   this client, as your spec says).
6. `PATCH /attendance/sessions/{id}/status` with `{"status": "CLOSED"}` once
   faculty has reviewed the data on screen.
7. `POST /attendance/sessions/{id}/submit` with the reviewed records:
   `{"records": [{"student_id": "S2026001", "status": "PRESENT"}, ...]}`.
   Note: `student_id` here is each student's **public** ID string (like
   `S2026001`), not a database number. Any class roster member you don't
   include is automatically marked ABSENT by the backend — you don't need to
   send absentees explicitly.
8. If step 7 returns a 409, it means the session isn't `CLOSED` yet or was
   already submitted — show that message to the faculty member rather than a
   generic error.

### 6.4 HOD Desktop Application (Python/Tkinter)

- `GET /hod/me` for their own profile/department.
- `GET /gatepasses/pending` — already filtered to their department, oldest
  request first.
- `PATCH /gatepasses/{id}/approve` (remarks optional) or
  `PATCH /gatepasses/{id}/reject` (remarks **required** — the backend returns
  422 if missing).
- `GET /attendance/department` for departmental attendance sessions,
  `GET /analytics/overview` and `GET /analytics/attendance` for dashboards
  (these are automatically scoped to the HOD's own department — no need to
  pass a department filter).
- `POST /notifications` to publish — HODs can only target their own
  department (`audience_type: "DEPARTMENT"` with their department, or
  `"SEMESTER"`/`"SECTION"`/`"SPECIFIC_GROUP"` within it). Sending
  `"ALL_STUDENTS"` or another department's code returns 403 — surface that as
  "you can only notify your own department."

---

## 7. End-to-end smoke test

Once at least one client is wired up, walk through this manually to confirm
the whole chain works:

1. Log in as `fac_cse1` (faculty app) → create a session → activate → close →
   submit attendance for a couple of students.
2. Log in as `s2026001` (student web app, if that student is in the class you
   just submitted for) → check their attendance percentage updated.
3. Log in as `s2026001` → submit a gate pass request.
4. Log in as `hod_cse` (HOD app) → see the pending request → approve it.
5. Back in the student app → confirm the gate pass now shows "APPROVED."
6. Log in as `admin` (admin app) → check `/analytics/overview` reflects the
   new attendance and gate-pass numbers.

If all six steps work, the system is functioning end to end.

---

## 8. Moving toward production (later, not required now)

These aren't needed to get things working locally, but keep them in mind:

- Replace the sample data: don't run `python -m app.seed` against a real
  database — build proper "create student/faculty/department" endpoints (not
  yet included) or load real data another way.
- Set `ENVIRONMENT=production` in `.env`, use a strong unique
  `JWT_SECRET_KEY`, and set `CORS_ORIGINS` to your real deployed frontend
  URL(s) only.
- Put the backend behind HTTPS (e.g. via a reverse proxy like nginx or a
  managed platform) — never send login credentials over plain HTTP outside
  local development.
- Regenerate the Alembic migration as real DDL before the first production
  deploy (the README has the exact steps) rather than relying on the
  bootstrap migration.
- Consider adding refresh tokens, password reset, and account lockout after
  repeated failed logins — none of these exist yet.

---

## Quick reference

```bash
# Every time you come back to work on the backend:
cd campus-cod/backend
source .venv/bin/activate
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

If a client can't reach the backend, check in this order:
1. Is `uvicorn` actually running and showing no errors in its terminal?
2. Is the client using the right base URL and port (`localhost:8000`)?
3. For the web app only: is its origin listed in `.env`'s `CORS_ORIGINS`,
   and did you restart `uvicorn` after editing `.env`?
4. Is the `Authorization: Bearer <token>` header actually being sent, and is
   the token still fresh (default expiry: 60 minutes)?

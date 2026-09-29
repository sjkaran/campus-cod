# Smart Campus Backend (FastAPI + PostgreSQL)

Central API for the four clients (Student web, Admin / Faculty / HOD desktop apps). Modular monolith:
`Router -> Schema -> Service -> Repository -> SQLAlchemy -> PostgreSQL`. Clients never touch the DB.

Place this folder as `backend/` at the root of the `campus-cod` repo.

## Setup
```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
createdb smart_campus                                   # or create the DB / user in pgAdmin
cp .env.example .env                                    # edit DATABASE_URL and JWT_SECRET_KEY
alembic upgrade head
python -m app.seed                                      # dev data; add --reset to wipe & reseed
uvicorn app.main:app --reload                           # http://localhost:8000/docs
pytest                                                  # tests use in-memory SQLite, no Postgres needed
```
Dev credentials (also at the top of `app/seed.py`; **never use in production**):
`admin / Admin@12345`, `hod_cse / Hod@12345`, `fac_cse1 / Faculty@12345`, `s2026001 / Student@12345`.

## Roles and enforcement
All authorization is server-side (`app/core/dependencies.py`, `app/services/access.py`).
Object-level denial (someone else's gate pass/student/session) returns **404**, not 403, so IDs cannot be enumerated.
Role-level denial returns 403. A HOD passing `?department=` for another department gets 403.

## Endpoint catalog (all under `/api`)
| Area | Endpoint | Roles |
|---|---|---|
| Auth | `POST /auth/login`, `GET /auth/me` | public / any |
| Students | `GET /students`, `GET /students/me`, `GET /students/me/attendance`, `GET /students/{id}` | ADMIN,HOD / STUDENT / STUDENT / ADMIN,HOD,STUDENT(self) |
| Profiles | `GET /faculty/me`, `GET /hod/me`, `GET /admin/me`, `GET /admin/audit-logs` | FACULTY / HOD / ADMIN / ADMIN |
| Catalog | `GET /departments`, `/subjects`, `/academic-classes` | any authenticated |
| Attendance | `POST /attendance/sessions`, `GET /attendance/sessions/my`, `GET /attendance/sessions/{id}`, `PATCH /attendance/sessions/{id}/status`, `POST /attendance/sessions/{id}/submit` | FACULTY (detail also HOD, ADMIN) |
| | `GET /attendance/department`, `GET /attendance` | HOD, ADMIN |
| Gate pass | `POST /gatepasses`, `GET /gatepasses/my`, `PATCH /gatepasses/{id}/cancel` | STUDENT |
| | `GET /gatepasses/pending`, `PATCH /gatepasses/{id}/approve`, `PATCH /gatepasses/{id}/reject` | HOD |
| | `GET /gatepasses`, `GET /gatepasses/{id}` | ADMIN,HOD (id: + owner STUDENT) |
| Notifications | `GET /notifications`, `PATCH /notifications/{id}/read` | STUDENT |
| | `POST /notifications`, `GET /notifications/created-by-me` | ADMIN, HOD |
| | `GET /notifications/admin` | ADMIN |
| Analytics | `GET /analytics/overview`, `/attendance`, `/attendance/subjects` | ADMIN,HOD,FACULTY (scoped) |
| | `GET /analytics/attendance/departments`, `/gatepasses` | ADMIN,HOD |
| Reports | `GET /reports/attendance` (+`?format=csv`) | ADMIN,HOD,FACULTY(own) |
| | `GET /reports/students`, `/reports/gatepasses` | ADMIN,HOD |

Envelope: `{"data": ...}`; lists add `{"pagination": {page, page_size, total}}` (`?page=&page_size=`, max 100); errors `{"detail": "..."}`.

## Workflows
**Attendance:** faculty `POST /attendance/sessions` (DRAFT; must be assigned to subject+class; optional `external_session_id` = QR-system ID, unique)
-> `PATCH .../status {"status":"ACTIVE"}` -> `{"status":"CLOSED"}` -> `POST .../submit {"records":[{"student_id":"S2026001","status":"PRESENT"}]}`.
Students on the class roster who are not listed become ABSENT (server decides). Unknown-class student = 400, duplicate = 409, all in one transaction.
Percentages are computed only by the backend (`app/utils/calculations.py`) from SUBMITTED sessions.

**Gate pass:** student POST -> PENDING -> HOD (own department only) approve / reject (remarks required) -> student polls `GET /gatepasses/my`.
Review locks the row (`SELECT ... FOR UPDATE`), sets status + hod + timestamp in one transaction; second review = 409.

**Notifications:** audience via `audience_type` + `targets` rows (no per-student copies). A target matches a student when every non-null field
(department, semester, section, student) matches. HODs are confined to their department. Read state is per student.

## Client contract notes (please check against the four clients)
I could not read the client code, so these are decisions made from the spec; compare them with your mock services:
- IDs in paths are numeric DB ids; students are identified in attendance submissions and notification targets by their **public** `student_id` (e.g. `S2026001`).
- `POST /auth/login` is JSON (`{"username","password"}`), returns `{access_token, token_type, expires_in, user}` (not wrapped in `data`). The submit endpoint returns the unwrapped `{success, session_id, status, ...}` shape from the spec.
- Extras beyond the spec's list, needed by the clients: session status endpoint, gate-pass cancel/list, `/faculty|hod|admin/me`, catalog endpoints, audit-log listing, `?format=csv`.
- Students get 403 on `/analytics/*`; their personal numbers come from `/students/me/attendance`.

## Known limitations
- **Not executed in the authoring environment** (no network/packages there): code was syntax-checked only. Run `pytest` first and expect small fixes.
- `alembic/versions/0001_initial_schema.py` builds tables via `metadata.create_all`. Freeze it before production: drop the DB, delete 0001, run `alembic revision --autogenerate -m "initial schema"`, review, `alembic upgrade head`.
- No endpoints yet to create/edit students, faculty, departments, subjects or assignments (seed only). No password change/reset, refresh tokens, rate limiting or account lockout.
- One HOD per department; gate passes have no overlap/duplicate detection.
- Docker not included (spec: optional).

# Smart Campus — Attendance Faculty Node (Stage 1)

## Run
    pip install -r requirements.txt      # qrcode + Pillow (app still runs without; shows token text)
    python main.py
Mock login: **FAC001 / faculty123**

## Test a session
New Session → pick class + subject → Start → use "Valid / Duplicate / Invalid" demo buttons →
Close Session → Finalize → Submit to Smart Campus → Export CSV. Set `MOCK_SUBMIT_FAILS=True` in `config/settings.py` to see SUBMISSION_FAILED + retry.

## Architecture
UI (`ui/`) → `services/campus_service.py` → `api/api_client.py` (mock) and `qr/` (QR adapter). Mock data lives only in `mock/`.
Status flow: ACTIVE → CLOSED → READY_FOR_SUBMISSION → SUBMITTED / SUBMISSION_FAILED.

## IMPORTANT: existing QR project not yet integrated
`deskapk/` from smart-Qr-attendance-system was not inspected. `qr/session_manager.py` and `qr/generator.py` are
stand-ins (rotating signed token, expiry, duplicate blocking). Port the real deskapk QR/session/report logic there,
keeping the public methods `token()`, `mark()`, `remaining()`, `close()`, and `qr_photo()`.

## Stage 2 replacement points (all in `api/api_client.py`)
login → POST /api/auth/login · get_subjects → GET /api/faculty/subjects · get_groups → GET /api/faculty/classes ·
get_students → GET /api/faculty/classes/{id}/students · list_reports → GET /api/attendance/sessions/my ·
save_report/session creation → POST /api/attendance/sessions · submit_report → POST /api/attendance/sessions/{id}/submit
Server must independently re-validate faculty, session, student, QR validity and duplicates.

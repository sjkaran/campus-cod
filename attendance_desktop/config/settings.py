"""Central configuration. No API URLs or secrets anywhere else."""
import os

APP_NAME = "Smart Campus — Attendance Faculty"
USE_MOCK_API = False                # Stage 2: live HttpApiClient
API_BASE_URL = os.environ.get("ATTENDANCE_API_BASE_URL", "https://discerning-liberation-production-e871.up.railway.app")
QR_ROTATE_SECONDS = 30              # QR payload rotation (adapter-level)
DEFAULT_SESSION_MINUTES = 10        # QR acceptance window shown in UI
MOCK_SUBMIT_FAILS = False           # flip to True to test SUBMISSION_FAILED
COLORS = dict(bg="#f4f6fa", side="#1f2a44", side_fg="#c9d3ea", accent="#2f6fed",
              card="#ffffff", ok="#1e9e5a", warn="#d98a00", bad="#d64545", text="#1c2233", muted="#6b7488")

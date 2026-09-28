"""Central configuration. No API URLs or secrets anywhere else."""
APP_NAME = "Smart Campus — Attendance Faculty"
USE_MOCK_API = True                 # Stage 2: set False -> HttpApiClient
API_BASE_URL = "http://localhost:8000"   # FUTURE API INTEGRATION
QR_ROTATE_SECONDS = 30              # QR payload rotation (adapter-level)
DEFAULT_SESSION_MINUTES = 10        # QR acceptance window shown in UI
MOCK_SUBMIT_FAILS = False           # flip to True to test SUBMISSION_FAILED
COLORS = dict(bg="#f4f6fa", side="#1f2a44", side_fg="#c9d3ea", accent="#2f6fed",
              card="#ffffff", ok="#1e9e5a", warn="#d98a00", bad="#d64545", text="#1c2233", muted="#6b7488")

"""
Application-wide configuration and constants for the HOD Desktop Application.

Keeping these values centralized means colors, fonts, sizes, and the
data-source mode (mock vs. future API) never need to be hunted down
across UI files.
"""

APP_NAME = "Smart Campus — HOD Portal"
APP_VERSION = "0.1.0-stage1"

WINDOW_MIN_WIDTH = 1180
WINDOW_MIN_HEIGHT = 720

# Stage 1 = mock data layer. Stage 2 flips this to "api" once the
# FastAPI backend exists; services/*.py read this flag to decide
# whether to call mock/mock_data.py or api/api_client.py.
DATA_SOURCE_MODE = "mock"  # "mock" | "api"

# Placeholder — populated from config/env in Stage 2.
API_BASE_URL = "https://api.smartcampus.local"


class Colors:
    """Central palette. ttk styles in ui/theme.py read from here."""

    BG = "#F4F6F9"
    SIDEBAR_BG = "#12233F"
    SIDEBAR_BG_ACTIVE = "#1B345C"
    SIDEBAR_TEXT = "#C9D6EA"
    SIDEBAR_TEXT_ACTIVE = "#FFFFFF"

    HEADER_BG = "#FFFFFF"
    CARD_BG = "#FFFFFF"
    BORDER = "#E1E6ED"

    TEXT_PRIMARY = "#1B2733"
    TEXT_SECONDARY = "#5B6B7C"
    TEXT_MUTED = "#8B99A8"

    PRIMARY = "#1C4E9C"
    PRIMARY_DARK = "#153E7D"
    ACCENT = "#2E7DD1"

    SUCCESS = "#1D9A6C"
    SUCCESS_BG = "#E4F6EF"
    WARNING = "#B7791F"
    WARNING_BG = "#FBF0DD"
    DANGER = "#C23B3B"
    DANGER_BG = "#FBE7E7"
    PENDING = "#B7791F"
    PENDING_BG = "#FBF0DD"

    ATTN_GOOD = "#1D9A6C"
    ATTN_NORMAL = "#B7791F"
    ATTN_LOW = "#C23B3B"


class Fonts:
    FAMILY = "Segoe UI"
    FALLBACK = "Helvetica"

    H1 = (FAMILY, 20, "bold")
    H2 = (FAMILY, 14, "bold")
    H3 = (FAMILY, 11, "bold")
    BODY = (FAMILY, 10)
    BODY_BOLD = (FAMILY, 10, "bold")
    SMALL = (FAMILY, 9)
    SMALL_BOLD = (FAMILY, 9, "bold")
    STAT = (FAMILY, 26, "bold")


# Attendance presentation thresholds — UI display rules only.
# The eventual backend provides the authoritative calculation.
ATTENDANCE_GOOD_THRESHOLD = 90
ATTENDANCE_NORMAL_THRESHOLD = 75

NAV_ITEMS = [
    ("dashboard", "Dashboard"),
    ("gatepass", "Gate Pass"),
    ("notifications", "Notifications"),
    ("attendance", "Attendance"),
    ("analytics", "Analytics"),
    ("reports", "Reports"),
    ("settings", "Settings"),
]

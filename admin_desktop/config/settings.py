"""
Application-wide configuration.

Centralizes theme tokens, spacing, fonts, feature thresholds and
environment-style settings so they are never hard-coded/scattered
across UI modules.
"""

import os

APP_NAME = "Smart Campus Admin"
APP_VERSION = "2.0.0-stage2"

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
WINDOW_MIN_WIDTH = 1180
WINDOW_MIN_HEIGHT = 720
WINDOW_DEFAULT_WIDTH = 1360
WINDOW_DEFAULT_HEIGHT = 820

# ---------------------------------------------------------------------------
# Color palette (professional, muted, blue/slate admin theme)
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#F4F6F9",              # app background
    "surface": "#FFFFFF",         # cards / panels
    "surface_alt": "#F9FAFC",     # table stripe / subtle panel
    "border": "#E2E6EC",
    "sidebar_bg": "#111827",      # near-black slate
    "sidebar_bg_active": "#1F2937",
    "sidebar_text": "#CBD5E1",
    "sidebar_text_active": "#FFFFFF",
    "sidebar_accent": "#3B82F6",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_text": "#FFFFFF",
    "text": "#111827",
    "text_muted": "#6B7280",
    "text_subtle": "#9CA3AF",
    "success": "#059669",
    "success_bg": "#ECFDF5",
    "warning": "#D97706",
    "warning_bg": "#FFFBEB",
    "danger": "#DC2626",
    "danger_bg": "#FEF2F2",
    "info": "#2563EB",
    "info_bg": "#EFF6FF",
    "neutral_bg": "#F1F5F9",
    "neutral_text": "#475569",
}

FONT_FAMILY = "Segoe UI"
FONT_FAMILY_FALLBACK = "Helvetica"

FONTS = {
    "h1": (FONT_FAMILY, 20, "bold"),
    "h2": (FONT_FAMILY, 15, "bold"),
    "h3": (FONT_FAMILY, 12, "bold"),
    "body": (FONT_FAMILY, 10),
    "body_bold": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9),
    "small_bold": (FONT_FAMILY, 9, "bold"),
    "kpi_value": (FONT_FAMILY, 22, "bold"),
    "sidebar": (FONT_FAMILY, 10),
    "sidebar_title": (FONT_FAMILY, 13, "bold"),
}

PADDING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}

# ---------------------------------------------------------------------------
# Business / display configuration (Stage 1 mock values — backend will own
# this eventually via a configuration endpoint)
# ---------------------------------------------------------------------------
ATTENDANCE_WARNING_THRESHOLD = 75.0   # below this = "below threshold"
ATTENDANCE_CRITICAL_THRESHOLD = 65.0  # below this = "critically below threshold"

PAGE_SIZE = 25  # simulated pagination page size for large tables

# ---------------------------------------------------------------------------
# Stage 2 — live backend connection
# ---------------------------------------------------------------------------
# Override by setting the ADMIN_API_BASE_URL environment variable before
# launching the app, e.g. if the backend runs on another machine/port:
#   (Windows PowerShell)  $env:ADMIN_API_BASE_URL = "http://192.168.1.20:8000/api"
#   (macOS/Linux)         export ADMIN_API_BASE_URL="http://192.168.1.20:8000/api"
API_BASE_URL = os.environ.get("ADMIN_API_BASE_URL", "http://localhost:8000/api")
API_TIMEOUT_SECONDS = 10

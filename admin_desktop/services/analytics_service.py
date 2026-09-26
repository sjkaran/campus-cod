"""
Analytics service.

Stage 1: getAnalytics() -> mock.analytics
Stage 2: -> ApiClient -> GET /api/analytics/overview (+ sub-endpoints)
"""

from models.analytics import AnalyticsOverview
from mock.analytics import get_overview


def get_analytics() -> AnalyticsOverview:
    """FUTURE API INTEGRATION:
        GET /api/analytics/overview
        GET /api/analytics/attendance
        GET /api/analytics/attendance/departments
        GET /api/analytics/attendance/subjects
        GET /api/analytics/gatepasses
    """
    return get_overview()

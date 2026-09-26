"""
Auth service.

Stage 1:  authenticate_admin() -> MockAuthService (this module)
Stage 2:  authenticate_admin() -> ApiAuthService -> POST /api/auth/login

The UI only ever calls authenticate_admin(); it has no knowledge of mock
vs. real implementations.
"""

from config.settings import MOCK_ADMIN_CREDENTIALS
from models.admin import Admin

_MOCK_ADMIN_DIRECTORY = {
    "admin": Admin(
        admin_id="ADM001",
        username="admin",
        name="Ananya Deshpande",
        designation="Campus Administrator",
        department="Administration",
        email="ananya.deshpande@campus.edu",
    ),
    "campus.admin": Admin(
        admin_id="ADM002",
        username="campus.admin",
        name="Rajesh Kulkarni",
        designation="Senior Administrator",
        department="Administration",
        email="rajesh.kulkarni@campus.edu",
    ),
}


class AuthResult:
    def __init__(self, success: bool, admin: Admin | None = None, error: str | None = None):
        self.success = success
        self.admin = admin
        self.error = error


def authenticate_admin(username: str, password: str) -> AuthResult:
    """Validates credentials against the mock directory.

    FUTURE API INTEGRATION
        Replace body with:
            response = api_client.post("/api/auth/login", {"username": username, "password": password})
            -> parse JWT + admin profile from response
    """
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return AuthResult(success=False, error="Username and password are required.")

    expected_password = MOCK_ADMIN_CREDENTIALS.get(username)
    if expected_password is None or expected_password != password:
        return AuthResult(success=False, error="Invalid Admin ID or password.")

    admin = _MOCK_ADMIN_DIRECTORY.get(username)
    return AuthResult(success=True, admin=admin)

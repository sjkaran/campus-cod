"""
Auth service — Stage 2 (live backend).

authenticate_admin() calls POST /auth/login, enforces that only ADMIN-role
accounts may use this desktop app, then loads the admin's profile via
GET /admin/me. The UI (ui/login.py) is unchanged — it only ever calls
authenticate_admin() and reads AuthResult.
"""

from models.admin import Admin
from api.api_client import api_client, ApiClientError


class AuthResult:
    def __init__(self, success: bool, admin: Admin | None = None, error: str | None = None):
        self.success = success
        self.admin = admin
        self.error = error


def authenticate_admin(username: str, password: str) -> AuthResult:
    username = (username or "").strip()
    password = password or ""

    if not username or not password:
        return AuthResult(success=False, error="Username and password are required.")

    try:
        login_response = api_client.post("/auth/login", {"username": username, "password": password})
    except ApiClientError as e:
        return AuthResult(success=False, error=str(e))

    user = login_response.get("user", {})
    if user.get("role") != "ADMIN":
        return AuthResult(
            success=False,
            error="This application is for Admin accounts only. "
                  f"That login has the {user.get('role', 'UNKNOWN')} role.",
        )

    api_client.set_auth_token(login_response["access_token"])

    try:
        profile = api_client.get_data("/admin/me")
    except ApiClientError as e:
        api_client.clear_auth_token()
        return AuthResult(success=False, error=f"Logged in, but could not load the admin profile: {e}")

    admin = Admin(
        admin_id=profile.get("employee_id", user.get("username", "")),
        username=user.get("username", username),
        # The backend does not yet model designation/department/email for
        # admins — these are display-only placeholders until it does.
        name=profile.get("name") or username,
        designation="System Administrator",
        department="Administration",
        email=f"{user.get('username', username)}@campus.edu",
    )
    return AuthResult(success=True, admin=admin)


def logout() -> None:
    api_client.clear_auth_token()

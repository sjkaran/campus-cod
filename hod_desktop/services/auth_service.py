"""
Authentication service.

UI code (ui/login.py) only ever talks to this module — never to
mock_data or api_client directly. That keeps the swap from mock
credentials to real JWT auth confined to this one file.
"""

from config.settings import DATA_SOURCE_MODE
from mock.mock_data import MOCK_CREDENTIALS, MOCK_HOD


class AuthError(Exception):
    pass


def login(hod_id: str, password: str) -> dict:
    hod_id = hod_id.strip()
    if not hod_id or not password:
        raise AuthError("HOD ID and password are required.")

    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client, ApiClientError
        try:
            response = api_client.login(hod_id, password)
        except ApiClientError as e:
            raise AuthError(str(e))

        user = response.get("user", {})
        if user.get("role") != "HOD":
            raise AuthError(
                "This application is for HOD accounts only. "
                f"That login has the {user.get('role', 'UNKNOWN')} role."
            )

        api_client.set_auth_token(response["access_token"])

        return {
            "hod_id": user.get("username", hod_id),
            "name": user.get("name") or user.get("username", hod_id),
            "department": user.get("department_name", ""),
            "designation": "Head of Department",
        }

    # mock path
    expected = MOCK_CREDENTIALS.get(hod_id)
    if expected is None or expected != password:
        raise AuthError("Invalid HOD ID or password.")
    return dict(MOCK_HOD)


def logout():
    if DATA_SOURCE_MODE == "api":
        from api.api_client import api_client
        api_client.clear_auth_token()
    return True

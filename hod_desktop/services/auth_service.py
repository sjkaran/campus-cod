"""
Authentication service.

UI code (ui/login.py) only ever talks to this module — never to
mock_data or api_client directly. That keeps the swap from mock
credentials to real JWT auth confined to this one file.
"""

from mock.mock_data import MOCK_CREDENTIALS, MOCK_HOD


class AuthError(Exception):
    pass


def login(hod_id: str, password: str) -> dict:
    """
    Stage 1: validate against mock credentials.
    Stage 2: replace body with api_client.login(hod_id, password),
             store the returned JWT, and return the profile payload.

    Future API: POST /api/auth/login
    """
    hod_id = hod_id.strip()
    if not hod_id or not password:
        raise AuthError("HOD ID and password are required.")

    expected = MOCK_CREDENTIALS.get(hod_id)
    if expected is None or expected != password:
        raise AuthError("Invalid HOD ID or password.")

    return dict(MOCK_HOD)


def logout():
    """Stage 2: clear stored JWT / call a token-revocation endpoint if any."""
    return True

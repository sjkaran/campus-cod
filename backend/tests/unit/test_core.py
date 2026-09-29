import jwt
import pytest

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.models import SessionStatus
from app.services.attendance_service import ALLOWED_TRANSITIONS, FACULTY_SETTABLE
from app.utils.calculations import percentage, summarize


def test_password_hash_is_not_plaintext_and_verifies():
    h = hash_password("s3cret!")
    assert h != "s3cret!" and h.startswith("$argon2")
    assert verify_password("s3cret!", h)
    assert not verify_password("wrong", h)


def test_verify_against_missing_user_is_false():
    assert verify_password("anything", None) is False


def test_jwt_roundtrip_carries_user_and_role():
    token, ttl = create_access_token(42, "HOD")
    payload = decode_access_token(token)
    assert payload["sub"] == "42" and payload["role"] == "HOD" and ttl > 0


def test_jwt_tampered_or_wrong_secret_rejected():
    forged = jwt.encode({"sub": "1", "role": "ADMIN"}, "another-secret-another-secret-123456", algorithm=settings.jwt_algorithm)
    with pytest.raises(UnauthorizedError):
        decode_access_token(forged)


def test_percentage_and_summary():
    assert percentage(34, 40) == 85.0
    assert percentage(0, 0) == 0.0
    s = summarize(40, 34)
    assert (s.total_classes, s.present, s.absent, s.percentage) == (40, 34, 6, 85.0)


def test_session_state_machine_is_linear_and_submit_is_reserved():
    assert ALLOWED_TRANSITIONS[SessionStatus.DRAFT] == {SessionStatus.ACTIVE, SessionStatus.CANCELLED}
    assert SessionStatus.SUBMITTED not in FACULTY_SETTABLE
    assert SessionStatus.SUBMITTED not in ALLOWED_TRANSITIONS  # terminal
    assert SessionStatus.CANCELLED not in ALLOWED_TRANSITIONS  # terminal

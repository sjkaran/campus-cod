"""Reusable input-validation helpers for forms across the Admin UI."""

import re
from datetime import datetime

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_non_empty(value: str) -> bool:
    return bool(value and value.strip())


def is_valid_email(value: str) -> bool:
    return bool(value) and bool(_EMAIL_RE.match(value.strip()))


def is_valid_date(value: str, fmt: str = "%Y-%m-%d") -> bool:
    if not value:
        return False
    try:
        datetime.strptime(value.strip(), fmt)
        return True
    except ValueError:
        return False


def is_valid_date_range(start: str, end: str, fmt: str = "%Y-%m-%d") -> bool:
    if not (is_valid_date(start, fmt) and is_valid_date(end, fmt)):
        return False
    return datetime.strptime(start, fmt) <= datetime.strptime(end, fmt)


def validate_login_form(username: str, password: str) -> list[str]:
    """Returns a list of human-readable error messages (empty = valid)."""
    errors = []
    if not is_non_empty(username):
        errors.append("Admin ID / Username is required.")
    if not is_non_empty(password):
        errors.append("Password is required.")
    return errors


def validate_notification_form(title: str, message: str, audience: str,
                                 publish_date: str, expiration_date: str) -> list[str]:
    errors = []
    if not is_non_empty(title):
        errors.append("Title is required.")
    elif len(title.strip()) > 120:
        errors.append("Title must be 120 characters or fewer.")
    if not is_non_empty(message):
        errors.append("Message is required.")
    if not is_non_empty(audience):
        errors.append("Audience must be selected.")
    if publish_date and not is_valid_date(publish_date):
        errors.append("Publish date must be in YYYY-MM-DD format.")
    if expiration_date and not is_valid_date(expiration_date):
        errors.append("Expiration date must be in YYYY-MM-DD format.")
    if publish_date and expiration_date and is_valid_date(publish_date) and is_valid_date(expiration_date):
        if not is_valid_date_range(publish_date, expiration_date):
            errors.append("Expiration date must be on or after the publish date.")
    return errors

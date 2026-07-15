from __future__ import annotations

import re

from app.exceptions.base import ValidationApplicationException


_COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
_PHONE_RE = re.compile(r"^[+]?[-0-9() ]{7,20}$")


def validate_country_code(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    if not _COUNTRY_RE.match(normalized):
        raise ValidationApplicationException("Country must be a 2-letter ISO code")
    return normalized


def validate_phone_number(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not _PHONE_RE.match(normalized):
        raise ValidationApplicationException("Invalid phone number")
    return normalized


def validate_employee_id(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise ValidationApplicationException("Employee ID is required")
    return normalized


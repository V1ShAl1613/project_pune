from __future__ import annotations

import re


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
PHONE_PATTERN = re.compile(r"^[0-9+()\-\s]{7,20}$")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_username(value: str) -> str:
    return value.strip().lower()


def validate_email_address(value: str) -> str:
    normalized = normalize_email(value)
    if not EMAIL_PATTERN.match(normalized):
        raise ValueError("Invalid email address")
    return normalized


def validate_username(value: str) -> str:
    normalized = normalize_username(value)
    if not USERNAME_PATTERN.match(normalized):
        raise ValueError("Username must be 3-64 characters and use letters, numbers, underscore, dash, or dot")
    return normalized


def validate_phone_number(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not PHONE_PATTERN.match(normalized):
        raise ValueError("Invalid phone number")
    return normalized


def validate_password_strength(password: str, minimum_length: int = 12) -> None:
    checks = [
        len(password) >= minimum_length,
        any(character.islower() for character in password),
        any(character.isupper() for character in password),
        any(character.isdigit() for character in password),
        any(not character.isalnum() for character in password),
    ]
    if not all(checks):
        raise ValueError(
            "Password must be at least 12 characters and include uppercase, lowercase, number, and symbol"
        )


def sanitize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

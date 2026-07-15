from __future__ import annotations

import pytest

from app.auth.security.password_hasher import PasswordHasher
from app.auth.tokens.service import JwtService
from app.auth.tokens.validator import TokenValidator
from app.auth.utils.validation import validate_email_address, validate_password_strength, validate_username
from app.core.settings import TestingSettings


def test_validation_helpers_accept_valid_values() -> None:
    assert validate_email_address("User@example.com") == "user@example.com"
    assert validate_username("john.doe") == "john.doe"
    validate_password_strength("Str0ng!Password")


def test_password_hasher_hash_and_verify() -> None:
    hasher = PasswordHasher()
    hashed = hasher.hash_password("Str0ng!Password")
    assert hasher.verify_password("Str0ng!Password", hashed)
    assert not hasher.verify_password("Wrong!Password", hashed)


def test_jwt_service_encode_decode_roundtrip() -> None:
    service = JwtService(TestingSettings())
    token = service.encode(service.create_claims(subject="123", token_type="access", expires_in=60))
    payload = service.decode(token)
    assert payload["sub"] == "123"
    assert payload["type"] == "access"


def test_token_validator_rejects_wrong_type() -> None:
    service = JwtService(TestingSettings())
    validator = TokenValidator(service)
    token = service.encode(service.create_claims(subject="123", token_type="refresh", expires_in=60))
    with pytest.raises(Exception):
        validator.validate_access_token(token)

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.auth.utils.validation import (
    normalize_email,
    normalize_username,
    validate_email_address,
    validate_password_strength,
    validate_phone_number,
    validate_username,
)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    username: str
    display_name: str
    password: str
    phone_number: str | None = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return validate_email_address(value)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        return validate_username(value)

    @field_validator("phone_number")
    @classmethod
    def _validate_phone_number(cls, value: str | None) -> str | None:
        return validate_phone_number(value)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value

    @model_validator(mode="after")
    def normalize(self) -> "RegisterRequest":
        self.email = normalize_email(self.email)
        self.username = normalize_username(self.username)
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str
    password: str
    device_id: str | None = None
    device_name: str | None = None
    device_fingerprint: str | None = None


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str | None = None


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return validate_email_address(value)


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class EmailVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    email: str
    username: str
    display_name: str
    phone_number: str | None
    status: str
    email_verified_at: datetime | None
    last_login_at: datetime | None


class AuthSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    status: str
    session_token: str
    expires_at: datetime
    last_seen_at: datetime | None
    last_activity_at: datetime | None
    ip_address: str | None
    user_agent: str | None
    device_id: str | None
    device_name: str | None


class AuthTokensResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_in: int = Field(ge=1)
    refresh_expires_in: int = Field(ge=1)


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: AuthUserResponse
    verification_email_sent: bool
    message: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: AuthUserResponse
    session: AuthSessionResponse
    tokens: AuthTokensResponse
    message: str


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session: AuthSessionResponse


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


class ProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: AuthUserResponse

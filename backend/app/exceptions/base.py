from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BaseApplicationException(Exception):
    message: str
    status_code: int = 500
    error_code: str = "application_error"
    details: dict[str, object] | None = None


class ValidationApplicationException(BaseApplicationException):
    status_code = 422
    error_code = "validation_error"


class AuthenticationApplicationException(BaseApplicationException):
    status_code = 401
    error_code = "authentication_error"


class AuthorizationApplicationException(BaseApplicationException):
    status_code = 403
    error_code = "authorization_error"


class DatabaseApplicationException(BaseApplicationException):
    status_code = 503
    error_code = "database_error"

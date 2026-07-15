from __future__ import annotations

from contextvars import ContextVar


correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")
request_path_var: ContextVar[str] = ContextVar("request_path", default="-")


def set_correlation_id(value: str) -> None:
    correlation_id_var.set(value)


def get_correlation_id() -> str:
    return correlation_id_var.get()


def set_request_path(value: str) -> None:
    request_path_var.set(value)


def get_request_path() -> str:
    return request_path_var.get()

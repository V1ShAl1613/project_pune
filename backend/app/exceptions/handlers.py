from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.base import BaseApplicationException
from app.schemas.common import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(BaseApplicationException, handle_base_application_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)


async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = ErrorResponse(
        error_code="validation_error",
        message="Request validation failed",
        details={"errors": exc.errors()},
    )
    return JSONResponse(payload.model_dump(), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    payload = ErrorResponse(
        error_code="http_error",
        message=str(exc.detail),
        details={"status_code": exc.status_code},
    )
    return JSONResponse(payload.model_dump(), status_code=exc.status_code)


async def handle_base_application_exception(request: Request, exc: BaseApplicationException) -> JSONResponse:
    payload = ErrorResponse(error_code=exc.error_code, message=exc.message, details=exc.details or {})
    return JSONResponse(payload.model_dump(), status_code=exc.status_code)


async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("sentinel.error").exception("unexpected_exception", extra={"path": request.url.path})
    payload = ErrorResponse(error_code="internal_server_error", message="Internal server error", details={})
    return JSONResponse(payload.model_dump(), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import provide_auth_context, provide_auth_service, provide_optional_auth_context
from app.auth.models import AuthContext
from app.auth.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MessageResponse,
    ProfileResponse,
    RefreshRequest,
    RegisterRequest,
    RegistrationResponse,
    ResetPasswordRequest,
    SessionResponse,
)
from app.auth.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegistrationResponse)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(provide_auth_service)) -> RegistrationResponse:
    return await auth_service.register(request)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(provide_auth_service)) -> LoginResponse:
    return await auth_service.login(request)


@router.post("/refresh", response_model=LoginResponse)
async def refresh(request: RefreshRequest, auth_service: AuthService = Depends(provide_auth_service)) -> LoginResponse:
    return await auth_service.refresh(request)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: LogoutRequest,
    auth_context: AuthContext | None = Depends(provide_optional_auth_context),
    auth_service: AuthService = Depends(provide_auth_service),
) -> MessageResponse:
    return await auth_service.logout(request, auth_context)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(provide_auth_service),
) -> MessageResponse:
    return await auth_service.forgot_password(request)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(provide_auth_service),
) -> MessageResponse:
    return await auth_service.reset_password(request)


@router.get("/profile", response_model=ProfileResponse)
async def profile(
    auth_context: AuthContext = Depends(provide_auth_context),
    auth_service: AuthService = Depends(provide_auth_service),
) -> ProfileResponse:
    return await auth_service.get_profile(auth_context)


@router.get("/session", response_model=SessionResponse)
async def session(
    auth_context: AuthContext = Depends(provide_auth_context),
    auth_service: AuthService = Depends(provide_auth_service),
) -> SessionResponse:
    return await auth_service.get_session(auth_context)


@router.delete("/session", response_model=MessageResponse)
async def delete_session(
    auth_context: AuthContext = Depends(provide_auth_context),
    auth_service: AuthService = Depends(provide_auth_service),
) -> MessageResponse:
    return await auth_service.revoke_current_session(auth_context)

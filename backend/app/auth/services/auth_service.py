from __future__ import annotations

import asyncio
import logging
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.auth.emails.smtp import SmtpEmailClient
from app.auth.emails.templates import reset_password_email_template, verification_email_template, welcome_email_template
from app.auth.models import AuthContext, AuthRequestContext
from app.auth.repositories.auth_repository import AuthRepository
from app.auth.schemas.auth import (
    AuthSessionResponse,
    AuthTokensResponse,
    AuthUserResponse,
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
from app.auth.security.password_hasher import PasswordHasher
from app.auth.tokens.generator import TokenGenerator
from app.auth.tokens.repository import TokenRepository
from app.auth.tokens.service import JwtService
from app.auth.tokens.validator import TokenValidator
from app.auth.utils.devices import RequestDeviceMetadata, build_device_metadata
from app.auth.utils.serialization import from_json, to_json
from app.auth.utils.validation import normalize_email, normalize_username, sanitize_text, validate_password_strength
from app.core.settings import AppSettings
from app.exceptions.base import AuthenticationApplicationException, BaseApplicationException
from app.database.models import AuditLog
from app.database.models.identity import RefreshToken, Session as AuthSession, User


@dataclass(slots=True)
class AuthService:
    repository: AuthRepository
    settings: AppSettings
    jwt_service: JwtService
    token_generator: TokenGenerator
    token_validator: TokenValidator
    token_repository: TokenRepository
    password_hasher: PasswordHasher
    email_client: SmtpEmailClient
    logger: logging.Logger
    audit_logger: logging.Logger

    async def register(
        self,
        request: RegisterRequest,
        context: AuthRequestContext | None = None,
    ) -> RegistrationResponse:
        display_name = sanitize_text(request.display_name)
        email = normalize_email(request.email)
        username = normalize_username(request.username)
        validate_password_strength(request.password, self.settings.password_min_length)
        existing_user = await self.repository.find_user_by_email(email)
        if existing_user is not None or await self.repository.find_user_by_identifier(username) is not None:
            raise BaseApplicationException("User already exists", status_code=409, error_code="user_conflict")

        now = datetime.now(UTC)
        password_hash = self.password_hasher.hash_password(request.password)
        password_expires_at = now + timedelta(days=self.settings.password_expiration_days)
        user = User(
            email=email,
            username=username,
            display_name=display_name,
            phone_number=request.phone_number,
            status="active",
            password_hash=password_hash,
            password_changed_at=now,
            password_expires_at=password_expires_at,
            password_history=[password_hash],
            profile={"registration_source": "auth_service"},
            authentication_metadata=self._request_metadata(context),
        )

        verification_sent = False
        verification_token = self._create_one_time_token("email_verification", request.email, user.email)
        verification_hash = self.jwt_service.hash_token(verification_token)
        verification_expires_at = now + timedelta(minutes=self.settings.verification_token_ttl_minutes)

        async with self.repository.transaction():
            user = await self.repository.create_user(user)
            await self.repository.update_user(
                user,
                {
                    "verification_token_hash": verification_hash,
                    "verification_token_expires_at": verification_expires_at,
                },
            )
            await self.token_repository.store_one_time_token(
                "verification",
                verification_hash,
                {"user_id": str(user.id), "email": user.email},
                self.settings.verification_token_ttl_minutes * 60,
            )
            verification_sent = self.email_client.send(
                user.email,
                verification_email_template(user.display_name, verification_token),
            )
            self.email_client.send(user.email, welcome_email_template(user.display_name))
            await self._write_audit_event(
                action="registration",
                user=user,
                context=context,
                details={"verification_sent": verification_sent},
            )

        return RegistrationResponse(
            user=AuthUserResponse.model_validate(user, from_attributes=True),
            verification_email_sent=verification_sent,
            message="Registration successful",
        )

    async def login(
        self,
        request: LoginRequest,
        context: AuthRequestContext | None = None,
    ) -> LoginResponse:
        identifier = request.identifier.strip().lower()
        user = await self.repository.find_user_by_identifier(identifier)
        if user is None:
            await self._handle_failed_login(identifier, context, None)
            raise AuthenticationApplicationException("Invalid credentials")

        if await self._is_locked(user, identifier):
            raise BaseApplicationException("Account temporarily locked", status_code=423, error_code="account_locked")

        if not self.password_hasher.verify_password(request.password, user.password_hash):
            await self._handle_failed_login(identifier, context, user)
            raise AuthenticationApplicationException("Invalid credentials")

        if user.password_expires_at is not None and user.password_expires_at <= datetime.now(UTC):
            raise BaseApplicationException("Password expired", status_code=403, error_code="password_expired")

        return await self._create_login_session(user, request, context)

    async def refresh(self, request: RefreshRequest, context: AuthRequestContext | None = None) -> LoginResponse:
        refresh_context = self.token_validator.validate_refresh_token(request.refresh_token)
        token_hash = self.jwt_service.hash_token(request.refresh_token)
        if await self.token_repository.is_refresh_token_revoked(token_hash):
            raise AuthenticationApplicationException("Refresh token revoked")

        refresh_record = await self.repository.get_refresh_token_by_jti(refresh_context.refresh_token_jti or "")
        if refresh_record is None or refresh_record.status != "active":
            raise AuthenticationApplicationException("Refresh token invalid")

        user = await self.repository.find_user_by_id(refresh_record.user_id)
        session = await self.repository.get_session_by_id(refresh_record.session_id)
        if user is None or session is None or session.status != "active":
            raise AuthenticationApplicationException("Refresh token invalid")

        async with self.repository.transaction():
            await self.repository.revoke_refresh_token(refresh_record, reason="rotation")
            await self.token_repository.revoke_refresh_token(token_hash, self.settings.refresh_token_ttl_days * 24 * 60 * 60)
            return await self._issue_session_tokens(
                user,
                session,
                context,
                refresh_family=refresh_record.family_id,
                rotated_from_jti=refresh_record.jti,
            )

    async def logout(
        self,
        request: LogoutRequest,
        auth_context: AuthContext | None = None,
        context: AuthRequestContext | None = None,
    ) -> MessageResponse:
        async with self.repository.transaction():
            if request.refresh_token:
                refresh_context = self.token_validator.validate_refresh_token(request.refresh_token)
                token_hash = self.jwt_service.hash_token(request.refresh_token)
                refresh_record = await self.repository.get_refresh_token_by_jti(refresh_context.refresh_token_jti or "")
                if refresh_record is not None:
                    await self.repository.revoke_refresh_token(refresh_record, reason="logout")
                await self.token_repository.revoke_refresh_token(
                    token_hash,
                    self.settings.refresh_token_ttl_days * 24 * 60 * 60,
                )
                session = await self.repository.get_session_by_id(refresh_context.session_id)
                if session is not None:
                    await self.repository.revoke_session(session, reason="logout")
                    await self.token_repository.revoke_session(str(session.id), self.settings.session_absolute_timeout_hours * 3600)
            elif auth_context is not None:
                session = await self.repository.get_session_by_id(auth_context.session_id)
                if session is not None:
                    await self.repository.revoke_session(session, reason="logout")
                    await self.token_repository.revoke_session(str(session.id), self.settings.session_absolute_timeout_hours * 3600)
            else:
                raise AuthenticationApplicationException("Authentication required")

            await self._write_audit_event(action="logout", user=None, context=context, details={"logout": True})

        return MessageResponse(message="Logout successful")

    async def forgot_password(
        self,
        request: ForgotPasswordRequest,
        context: AuthRequestContext | None = None,
    ) -> MessageResponse:
        user = await self.repository.find_user_by_email(request.email)
        if user is not None:
            token = self._create_one_time_token("password_reset", str(user.id), user.email)
            token_hash = self.jwt_service.hash_token(token)
            expires_at = datetime.now(UTC) + timedelta(minutes=self.settings.reset_token_ttl_minutes)
            async with self.repository.transaction():
                await self.repository.update_user(
                    user,
                    {
                        "password_reset_token_hash": token_hash,
                        "password_reset_token_expires_at": expires_at,
                    },
                )
                await self.token_repository.store_one_time_token(
                    "reset",
                    token_hash,
                    {"user_id": str(user.id), "email": user.email},
                    self.settings.reset_token_ttl_minutes * 60,
                )
                self.email_client.send(
                    user.email,
                    reset_password_email_template(user.display_name, token),
                )
                await self._write_audit_event(action="forgot_password", user=user, context=context, details={})

        return MessageResponse(message="If the account exists, a reset email has been sent")

    async def reset_password(
        self,
        request: ResetPasswordRequest,
        context: AuthRequestContext | None = None,
    ) -> MessageResponse:
        payload = self.token_validator.validate_one_time_token(request.token, "password_reset")
        token_hash = self.jwt_service.hash_token(request.token)
        redis_payload = await self.token_repository.consume_one_time_token("reset", token_hash)
        user = await self.repository.find_user_by_id(payload["sub"])
        if user is None:
            raise AuthenticationApplicationException("Invalid reset token")
        if redis_payload is None or user.password_reset_token_hash != token_hash:
            raise AuthenticationApplicationException("Invalid reset token")
        if user.password_reset_token_expires_at is not None and user.password_reset_token_expires_at <= datetime.now(UTC):
            raise AuthenticationApplicationException("Reset token expired")

        if self.password_hasher.password_reused(request.new_password, list(user.password_history or [])):
            raise BaseApplicationException("Password reuse is not allowed", status_code=400, error_code="password_reuse")

        new_password_hash = self.password_hasher.hash_password(request.new_password)
        password_history = list(user.password_history or [])
        password_history.insert(0, user.password_hash)
        password_history = password_history[: self.settings.password_history_size]
        now = datetime.now(UTC)

        async with self.repository.transaction():
            await self.repository.update_user(
                user,
                {
                    "password_hash": new_password_hash,
                    "password_changed_at": now,
                    "password_expires_at": now + timedelta(days=self.settings.password_expiration_days),
                    "password_history": password_history,
                    "password_reset_token_hash": None,
                    "password_reset_token_expires_at": None,
                    "failed_login_count": 0,
                    "failed_login_at": None,
                    "locked_until": None,
                },
            )
            await self._revoke_user_sessions(user.id, reason="password_reset")
            await self._write_audit_event(action="password_reset", user=user, context=context, details={})

        return MessageResponse(message="Password reset successful")

    async def get_profile(self, auth_context: AuthContext) -> ProfileResponse:
        user = await self.repository.find_user_by_id(auth_context.user_id)
        if user is None:
            raise AuthenticationApplicationException("User not found")
        return ProfileResponse(user=AuthUserResponse.model_validate(user, from_attributes=True))

    async def get_session(self, auth_context: AuthContext) -> SessionResponse:
        session = await self.repository.get_session_by_id(auth_context.session_id)
        if session is None:
            raise AuthenticationApplicationException("Session not found")
        return SessionResponse(session=AuthSessionResponse.model_validate(session, from_attributes=True))

    async def revoke_current_session(self, auth_context: AuthContext, context: AuthRequestContext | None = None) -> MessageResponse:
        async with self.repository.transaction():
            session = await self.repository.get_session_by_id(auth_context.session_id)
            if session is None:
                raise AuthenticationApplicationException("Session not found")
            await self.repository.revoke_session(session, reason="session_delete")
            await self.token_repository.revoke_session(str(session.id), self.settings.session_absolute_timeout_hours * 3600)
            await self._write_audit_event(action="session_revocation", user=None, context=context, details={"session_id": str(session.id)})
        return MessageResponse(message="Session revoked")

    async def _create_login_session(
        self,
        user: User,
        request: LoginRequest,
        context: AuthRequestContext | None,
    ) -> LoginResponse:
        now = datetime.now(UTC)
        session = AuthSession(
            user_id=user.id,
            session_token=secrets.token_urlsafe(32),
            refresh_token_hash="",
            status="active",
            expires_at=now + timedelta(hours=self.settings.session_absolute_timeout_hours),
            last_seen_at=now,
            last_activity_at=now,
            ip_address=context.ip_address if context else None,
            user_agent=context.user_agent if context else None,
            device_id=request.device_id,
            device_name=request.device_name,
            device_fingerprint=request.device_fingerprint,
            geo_location=(context.geo_location if context and context.geo_location else {"country": None, "region": None, "city": None}),
            session_metadata={"login": True, "device": request.device_name},
        )
        async with self.repository.transaction():
            session = await self.repository.create_session(session)
            return await self._issue_session_tokens(user, session, context)

    async def _issue_session_tokens(
        self,
        user: User,
        session: AuthSession,
        context: AuthRequestContext | None,
        *,
        refresh_family: str | None = None,
        rotated_from_jti: str | None = None,
    ) -> LoginResponse:
        tokens = self.token_generator.generate_token_pair(user, session, family_id=refresh_family)
        refresh_hash = self.jwt_service.hash_token(tokens.refresh_token)
        refresh_expires_at = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_ttl_days)
        refresh_token = RefreshToken(
            user_id=user.id,
            session_id=session.id,
            jti=tokens.refresh_jti,
            family_id=refresh_family or tokens.family_id,
            rotated_from_jti=rotated_from_jti,
            token_hash=refresh_hash,
            status="active",
            expires_at=refresh_expires_at,
            token_metadata=self._request_metadata(context),
        )
        await self.repository.create_refresh_token(refresh_token)
        await self.repository.update_session(
            session,
            {
                "refresh_token_hash": refresh_hash,
                "last_activity_at": datetime.now(UTC),
                "last_seen_at": datetime.now(UTC),
            },
        )
        await self.repository.update_user(
            user,
            {
                "last_login_at": datetime.now(UTC),
                "last_login_ip": context.ip_address if context else None,
                "last_login_user_agent": context.user_agent if context else None,
                "failed_login_count": 0,
                "failed_login_at": None,
                "locked_until": None,
            },
        )
        await self.token_repository.store_refresh_token(
            refresh_hash,
            {
                "user_id": str(user.id),
                "session_id": str(session.id),
                "jti": tokens.refresh_jti,
                "family_id": refresh_family or tokens.family_id,
            },
            self.settings.refresh_token_ttl_days * 24 * 60 * 60,
        )
        await self.token_repository.store_session(
            str(session.id),
            {
                "user_id": str(user.id),
                "session_id": str(session.id),
                "device_name": session.device_name,
                "device_id": session.device_id,
            },
            self.settings.session_absolute_timeout_hours * 3600,
        )
        await self._enforce_session_limit(user.id)
        await self._write_audit_event(action="login", user=user, context=context, details={"session_id": str(session.id)})

        return LoginResponse(
            user=AuthUserResponse.model_validate(user, from_attributes=True),
            session=AuthSessionResponse.model_validate(session, from_attributes=True),
            tokens=AuthTokensResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                access_expires_in=tokens.access_expires_in,
                refresh_expires_in=tokens.refresh_expires_in,
            ),
            message="Login successful",
        )

    async def _revoke_user_sessions(self, user_id, *, reason: str) -> None:
        sessions = await self.repository.list_active_sessions(user_id)
        for session in sessions:
            await self.repository.revoke_session(session, reason=reason)
            await self.token_repository.revoke_session(str(session.id), self.settings.session_absolute_timeout_hours * 3600)

    async def _enforce_session_limit(self, user_id) -> None:
        sessions = await self.repository.list_active_sessions(user_id)
        if len(sessions) <= self.settings.max_concurrent_sessions:
            return
        for session in sessions[self.settings.max_concurrent_sessions :]:
            await self.repository.revoke_session(session, reason="session_limit")
            await self.token_repository.revoke_session(str(session.id), self.settings.session_absolute_timeout_hours * 3600)

    async def _handle_failed_login(self, identifier: str, context: AuthRequestContext | None, user: User | None) -> None:
        await asyncio.sleep(min(self.settings.max_login_delay_seconds, 0.1))
        async with self.repository.transaction():
            if user is not None:
                failures = user.failed_login_count + 1
                locked_until = None
                if failures >= self.settings.login_failure_threshold:
                    locked_until = datetime.now(UTC) + timedelta(minutes=self.settings.account_lock_minutes)
                await self.repository.update_user(
                    user,
                    {
                        "failed_login_count": failures,
                        "failed_login_at": datetime.now(UTC),
                        "locked_until": locked_until,
                    },
                )
                if locked_until is not None:
                    await self.token_repository.lock_account(identifier, self.settings.account_lock_minutes * 60)
            else:
                await self.token_repository.increment_failed_login(identifier, self.settings.account_lock_minutes * 60)
            await self._write_audit_event(action="failed_login", user=user, context=context, details={"identifier": identifier})

    async def _is_locked(self, user: User, identifier: str) -> bool:
        if user.locked_until is not None and user.locked_until > datetime.now(UTC):
            return True
        return await self.token_repository.is_account_locked(identifier)

    def _create_one_time_token(self, token_type: str, subject: str, email: str) -> str:
        claims = self.jwt_service.create_claims(
            subject=subject,
            token_type=token_type,
            expires_in=(self.settings.verification_token_ttl_minutes if token_type == "email_verification" else self.settings.reset_token_ttl_minutes) * 60,
            extra_claims={"email": email},
        )
        return self.jwt_service.encode(claims)

    def _request_metadata(self, context: AuthRequestContext | None) -> dict[str, object]:
        if context is None:
            return {}
        return {
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
            "device_id": context.device_id,
            "device_name": context.device_name,
            "device_fingerprint": context.device_fingerprint,
            "geo_location": context.geo_location or {"country": None, "region": None, "city": None},
        }

    async def _write_audit_event(
        self,
        *,
        action: str,
        user: User | None,
        context: AuthRequestContext | None,
        details: dict[str, object],
    ) -> None:
        self.audit_logger.info(
            action,
            extra={
                "user_id": str(user.id) if user else None,
                "details": details,
                "context": self._request_metadata(context),
            },
        )
        await self.repository.create_audit_log(
            AuditLog(
                actor_user_id=user.id if user else None,
                entity_type="authentication",
                entity_id=str(user.id) if user else "anonymous",
                action=action,
                context={"details": details, **self._request_metadata(context)},
                request_path=None,
                request_method=None,
                status="success",
            )
        )

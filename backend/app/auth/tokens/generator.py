from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.auth.models import TokenPair
from app.auth.tokens.service import JwtService
from app.core.settings import AppSettings
from app.database.models.identity import Session, User


@dataclass(slots=True)
class TokenGenerator:
    settings: AppSettings
    jwt_service: JwtService

    def generate_token_pair(self, user: User, session: Session, family_id: str | None = None) -> TokenPair:
        resolved_family_id = family_id or secrets.token_urlsafe(16)
        access_expires_in = self.settings.access_token_ttl_minutes * 60
        refresh_expires_in = self.settings.refresh_token_ttl_days * 24 * 60 * 60
        access_jti = secrets.token_urlsafe(16)
        refresh_jti = secrets.token_urlsafe(16)

        access_claims = self.jwt_service.create_claims(
            subject=str(user.id),
            token_type="access",
            expires_in=access_expires_in,
            jti=access_jti,
            extra_claims={"sid": str(session.id), "family": resolved_family_id, "email": user.email, "username": user.username},
        )
        refresh_claims = self.jwt_service.create_claims(
            subject=str(user.id),
            token_type="refresh",
            expires_in=refresh_expires_in,
            jti=refresh_jti,
            extra_claims={"sid": str(session.id), "family": resolved_family_id},
        )

        return TokenPair(
            access_token=self.jwt_service.encode(access_claims),
            refresh_token=self.jwt_service.encode(refresh_claims),
            access_expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            family_id=resolved_family_id,
        )

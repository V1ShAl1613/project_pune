from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

try:  # pragma: no cover - optional dependency
    import bcrypt
except ModuleNotFoundError:  # pragma: no cover - fallback for lean environments
    bcrypt = None


@dataclass(slots=True)
class PasswordHasher:
    rounds: int = 12
    iterations: int = 310000

    def hash_password(self, password: str) -> str:
        if bcrypt is not None:
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return f"bcrypt${hashed.decode('utf-8')}"
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return "pbkdf2_sha256${}${}${}".format(
            self.iterations,
            base64.urlsafe_b64encode(salt).decode("utf-8"),
            base64.urlsafe_b64encode(derived).decode("utf-8"),
        )

    def verify_password(self, password: str, encoded: str) -> bool:
        if encoded.startswith("bcrypt$"):
            if bcrypt is None:
                return False
            stored = encoded.split("$", 1)[1].encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), stored)
        if encoded.startswith("pbkdf2_sha256$"):
            return self._verify_pbkdf2(password, encoded)
        return False

    def password_reused(self, password: str, history: list[str]) -> bool:
        return any(self.verify_password(password, hash_value) for hash_value in history)

    def _verify_pbkdf2(self, password: str, encoded: str) -> bool:
        _, iterations, salt_value, hash_value = encoded.split("$")
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            base64.urlsafe_b64decode(salt_value.encode("utf-8")),
            int(iterations),
        )
        expected = base64.urlsafe_b64decode(hash_value.encode("utf-8"))
        return hmac.compare_digest(derived, expected)

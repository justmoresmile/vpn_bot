import asyncio
import hashlib
import hmac
import secrets
import time

from app.config import settings
from app.repositories.email_auth_repository import (
    email_auth_repo,
)
from app.services.auth.jwt_service import jwt_service
from app.services.email_service import email_service
from app.services.user_service import user_service


class EmailAuthService:

    CODE_TTL_SECONDS = 600
    MAX_ATTEMPTS = 5
    REQUEST_COOLDOWN_SECONDS = 60

    # ==============================
    # NORMALIZE EMAIL
    # ==============================

    @staticmethod
    def normalize_email(
        email: str,
    ) -> str:

        return email.strip().lower()

    # ==============================
    # GENERATE CODE
    # ==============================

    @staticmethod
    def generate_code() -> str:

        return f"{secrets.randbelow(1_000_000):06d}"

    # ==============================
    # HASH CODE
    # ==============================

    @staticmethod
    def hash_code(
        email: str,
        code: str,
    ) -> str:

        email = EmailAuthService.normalize_email(
            email
        )

        message = (
            f"{email}:{code}"
        ).encode("utf-8")

        secret = settings.jwt_secret.encode(
            "utf-8"
        )

        return hmac.new(
            secret,
            message,
            hashlib.sha256,
        ).hexdigest()

    # ==============================
    # CREATE + SEND CODE
    # ==============================

    async def create_login_code(
        self,
        email: str,
    ) -> int:

        email = self.normalize_email(
            email
        )

        now = int(
            time.time()
        )

        last_created_at = (
            email_auth_repo.get_last_created_at(
                email
            )
        )

        if (
            last_created_at is not None
            and now - last_created_at
            < self.REQUEST_COOLDOWN_SECONDS
        ):
            retry_after = (
                self.REQUEST_COOLDOWN_SECONDS
                - (now - last_created_at)
            )

            raise RuntimeError(
                f"RATE_LIMIT:{retry_after}"
            )

        code = self.generate_code()

        code_hash = self.hash_code(
            email=email,
            code=code,
        )



        expires_at = (
            now
            + self.CODE_TTL_SECONDS
        )

        email_auth_repo.create_code(
            email=email,
            code_hash=code_hash,
            expires_at=expires_at,
        )

        try:

            await asyncio.to_thread(
                email_service.send_login_code,
                email,
                code,
            )

        except Exception:

            email_auth_repo.invalidate_codes(
                email=email,
                used_at=int(time.time()),
            )

            raise

        return self.CODE_TTL_SECONDS

    # ==============================
    # VERIFY CODE
    # ==============================

    def verify_login_code(
        self,
        email: str,
        code: str,
    ) -> str | None:

        email = self.normalize_email(
            email
        )

        now = int(
            time.time()
        )

        row = email_auth_repo.get_active_code(
            email=email,
            now=now,
        )

        if row is None:
            return None

        code_id = int(
            row["id"]
        )

        attempts = int(
            row["attempts"]
        )

        if attempts >= self.MAX_ATTEMPTS:

            email_auth_repo.mark_used(
                code_id=code_id,
                used_at=now,
            )

            return None

        expected_hash = row[
            "code_hash"
        ]

        actual_hash = self.hash_code(
            email=email,
            code=code,
        )

        if not hmac.compare_digest(
            expected_hash,
            actual_hash,
        ):

            email_auth_repo.increment_attempts(
                code_id
            )

            if (
                attempts + 1
                >= self.MAX_ATTEMPTS
            ):
                email_auth_repo.mark_used(
                    code_id=code_id,
                    used_at=now,
                )

            return None

        email_auth_repo.mark_used(
            code_id=code_id,
            used_at=now,
        )

        user = user_service.get_by_email(
            email
        )

        if user is None:

            user = (
                user_service.create_by_email(
                    email
                )
            )

        return jwt_service.create_token(
            user.id
        )


email_auth_service = EmailAuthService()
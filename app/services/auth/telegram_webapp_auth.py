import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from app.config import settings


class TelegramWebAppAuth:

    def validate_init_data(
        self,
        init_data: str,
    ) -> dict | None:

        try:
            parsed = dict(
                parse_qsl(
                    init_data,
                    keep_blank_values=True,
                )
            )

            received_hash = parsed.pop(
                "hash",
                None,
            )

            if not received_hash:
                return None

            data_check_string = "\n".join(
                f"{key}={value}"
                for key, value in sorted(
                    parsed.items()
                )
            )

            secret_key = hmac.new(
                b"WebAppData",
                settings.bot_token.encode(),
                hashlib.sha256,
            ).digest()

            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(
                calculated_hash,
                received_hash,
            ):
                return None

            user_raw = parsed.get("user")

            if not user_raw:
                return None

            user = json.loads(
                user_raw
            )

            return {
                "telegram_id": user["id"],
                "username": user.get(
                    "username"
                ),
                "first_name": user.get(
                    "first_name"
                ),
                "auth_date": parsed.get(
                    "auth_date"
                ),
            }

        except (
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ):
            return None


telegram_webapp_auth = TelegramWebAppAuth()
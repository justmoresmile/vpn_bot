from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.repositories.user_repository import UsersRepository
from app.services.remnawave_client import remnawave_client


DEFAULT_SQUAD_UUID = (
    "7ca43779-d4f6-4a5b-8fc2-6bee4f2a7be3"
)

DEFAULT_HWID_DEVICE_LIMIT = 1


class RemnawaveService:

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def build_username(
        justvpn_user_id: int,
    ) -> str:
        return f"u_{justvpn_user_id}"

    @staticmethod
    def _unwrap(
        data: Any,
    ) -> Any:
        if (
            isinstance(data, dict)
            and "response" in data
        ):
            return data["response"]

        return data

    @staticmethod
    def _format_datetime(
        value: datetime,
    ) -> str:

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=timezone.utc
            )

        value = value.astimezone(
            timezone.utc
        )

        return (
            value
            .isoformat(
                timespec="milliseconds"
            )
            .replace(
                "+00:00",
                "Z",
            )
        )

    # ==========================================================
    # GET USER
    # ==========================================================

    def get_user(
        self,
        justvpn_user_id: int,
    ) -> dict[str, Any] | None:

        username = self.build_username(
            justvpn_user_id
        )

        try:
            data = (
                remnawave_client
                .get_user_by_username(
                    username
                )
            )

        except httpx.HTTPStatusError as exc:

            if exc.response.status_code == 404:
                return None

            raise

        user = self._unwrap(data)

        if not isinstance(user, dict):
            raise RuntimeError(
                "Unexpected Remnawave user response"
            )

        return user

    # ==========================================================
    # DELETE USER
    # ==========================================================

    def delete_user(
        self,
        justvpn_user_id: int,
    ) -> bool:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return False

        remnawave_user_id = user.get(
            "id"
        )

        if not remnawave_user_id:
            raise RuntimeError(
                "Remnawave user id is missing"
            )

        remnawave_client.delete_user(
            int(remnawave_user_id)
        )

        return True

    # ==========================================================
    # CREATE USER
    # ==========================================================

    def create_user(
        self,
        *,
        justvpn_user_id: int,
        expire_at: datetime,
        email: str | None = None,
        telegram_id: int | None = None,
        hwid_device_limit: int = (
            DEFAULT_HWID_DEVICE_LIMIT
        ),
        squad_uuid: str = (
            DEFAULT_SQUAD_UUID
        ),
    ) -> dict[str, Any]:

        username = self.build_username(
            justvpn_user_id
        )

        payload: dict[str, Any] = {
            "username": username,

            "expireAt":
                self._format_datetime(
                    expire_at
                ),

            "trafficLimitBytes": 0,

            "trafficLimitStrategy":
                "NO_RESET",

            "hwidDeviceLimit":
                hwid_device_limit,

            "activeInternalSquads": [
                squad_uuid
            ],

            "description":
                f"JustVPN user #{justvpn_user_id}",
        }

        if email:
            payload["email"] = email

        if telegram_id:
            payload["telegramId"] = int(
                telegram_id
            )

        data = (
            remnawave_client
            .create_user(
                payload
            )
        )

        user = self._unwrap(data)

        if not isinstance(user, dict):
            raise RuntimeError(
                "Unexpected Remnawave create user response"
            )

        return user

    # ==========================================================
    # ENSURE USER
    # ==========================================================

    def ensure_user(
        self,
        *,
        justvpn_user_id: int,
        expire_at: datetime,
        email: str | None = None,
        telegram_id: int | None = None,
        hwid_device_limit: int = (
            DEFAULT_HWID_DEVICE_LIMIT
        ),
        squad_uuid: str = (
            DEFAULT_SQUAD_UUID
        ),
    ) -> dict[str, Any]:

        local_user = (
            UsersRepository.get_by_id(
                justvpn_user_id
            )
        )

        if local_user is None:
            raise RuntimeError(
                f"JustVPN user "
                f"{justvpn_user_id} not found"
            )

        # Если данные явно не переданы,
        # используем данные аккаунта JustVPN.
        if email is None:
            email = local_user.email

        if telegram_id is None:
            telegram_id = (
                local_user.telegram_id
            )

        username = self.build_username(
            justvpn_user_id
        )

        user = self.get_user(
            justvpn_user_id
        )

        # ------------------------------------------------------
        # CREATE
        # ------------------------------------------------------

        if user is None:

            user = self.create_user(
                justvpn_user_id=
                    justvpn_user_id,

                expire_at=
                    expire_at,

                email=
                    email,

                telegram_id=
                    telegram_id,

                hwid_device_limit=
                    hwid_device_limit,

                squad_uuid=
                    squad_uuid,
            )

        # ------------------------------------------------------
        # UPDATE
        # ------------------------------------------------------

        else:

            payload: dict[str, Any] = {
                "id": user["id"],

                "username":
                    username,

                "expireAt":
                    self._format_datetime(
                        expire_at
                    ),

                "trafficLimitBytes": 0,

                "trafficLimitStrategy":
                    "NO_RESET",

                "hwidDeviceLimit":
                    hwid_device_limit,

                "activeInternalSquads": [
                    squad_uuid
                ],

                "description":
                    (
                        f"JustVPN user "
                        f"#{justvpn_user_id}"
                    ),

                "email":
                    email,

                "telegramId":
                    (
                        int(telegram_id)
                        if telegram_id
                        is not None
                        else None
                    ),
            }

            data = (
                remnawave_client
                .update_user(
                    payload
                )
            )

            user = self._unwrap(
                data
            )

            if not isinstance(
                user,
                dict,
            ):
                raise RuntimeError(
                    "Unexpected Remnawave "
                    "update user response"
                )

        # ------------------------------------------------------
        # SAVE PROVIDER MAPPING
        # ------------------------------------------------------

        provider_user_id = user.get(
            "id"
        )

        if provider_user_id is None:
            raise RuntimeError(
                "Remnawave user response "
                "has no id"
            )

        provider_username = (
            user.get("username")
            or username
        )

        UsersRepository.set_vpn_provider(
            user_id=justvpn_user_id,
            provider="remnawave",
            provider_user_id=int(
                provider_user_id
            ),
            provider_username=str(
                provider_username
            ),
        )

        return user

    # ==========================================================
    # RENEW USER
    # ==========================================================

    def renew_user(
        self,
        *,
        justvpn_user_id: int,
        days: int,
    ) -> dict[str, Any]:

        if days <= 0:
            raise ValueError(
                "days must be greater than 0"
            )

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            raise RuntimeError(
                "Remnawave user not found"
            )

        current_expire_at = (
            user.get("expireAt")
        )

        now = datetime.now(
            timezone.utc
        )

        if current_expire_at:

            try:
                current_expire = (
                    datetime
                    .fromisoformat(
                        current_expire_at
                        .replace(
                            "Z",
                            "+00:00",
                        )
                    )
                )

            except ValueError:
                current_expire = now

        else:
            current_expire = now

        if current_expire < now:
            base = now
        else:
            base = current_expire

        new_expire_at = (
            base
            + timedelta(
                days=days
            )
        )

        payload = {
            "id": user["id"],

            "expireAt":
                self._format_datetime(
                    new_expire_at
                ),
        }

        data = (
            remnawave_client
            .update_user(
                payload
            )
        )

        updated = self._unwrap(data)

        if not isinstance(updated, dict):
            raise RuntimeError(
                "Unexpected Remnawave renew response"
            )

        return updated

    # ==========================================================
    # DISABLE USER
    # ==========================================================

    def disable_user(
        self,
        justvpn_user_id: int,
    ) -> dict[str, Any] | None:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return None

        data = (
            remnawave_client
            .request(
                "POST",
                (
                    f"/api/users/"
                    f"{user['id']}"
                    "/actions/disable"
                ),
            )
        )

        result = self._unwrap(data)

        if result is None:
            return None

        if not isinstance(
            result,
            dict,
        ):
            raise RuntimeError(
                "Unexpected Remnawave disable response"
            )

        return result

    # ==========================================================
    # ENABLE USER
    # ==========================================================

    def enable_user(
        self,
        justvpn_user_id: int,
    ) -> dict[str, Any] | None:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return None

        data = (
            remnawave_client
            .request(
                "POST",
                (
                    f"/api/users/"
                    f"{user['id']}"
                    "/actions/enable"
                ),
            )
        )

        result = self._unwrap(data)

        if result is None:
            return None

        if not isinstance(
            result,
            dict,
        ):
            raise RuntimeError(
                "Unexpected Remnawave enable response"
            )

        return result

    # ==========================================================
    # SUBSCRIPTION URL
    # ==========================================================

    def get_subscription_url(
        self,
        justvpn_user_id: int,
    ) -> str | None:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return None

        value = user.get(
            "subscriptionUrl"
        )

        if not value:
            return None

        return str(value)

    # ==========================================================
    # BANDWIDTH
    # ==========================================================

    def get_usage(
        self,
        justvpn_user_id: int,
        start: str,
        end: str,
    ) -> Any:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return None

        data = (
            remnawave_client
            .get_user_usage(
                user_id=int(
                    user["id"]
                ),
                start=start,
                end=end,
            )
        )

        return self._unwrap(
            data
        )

    # ==========================================================
    # DEVICES
    # ==========================================================

    def get_devices(
        self,
        justvpn_user_id: int,
    ) -> Any:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            return None

        data = (
            remnawave_client
            .get_devices(
                str(
                    user["id"]
                )
            )
        )

        return self._unwrap(
            data
        )


    def delete_device(
        self,
        justvpn_user_id: int,
        hwid: str,
    ) -> Any:

        user = self.get_user(
            justvpn_user_id
        )

        if user is None:
            raise ValueError(
                "Remnawave user not found"
            )

        data = (
            remnawave_client
            .delete_device(
                user_id=int(
                    user["id"]
                ),
                hwid=hwid,
            )
        )

        return self._unwrap(
            data
        )


remnawave_service = RemnawaveService()

from dataclasses import dataclass
import re

from fastapi import HTTPException, Request

from app.logger import logger
from app.repositories.device_repository import device_repo


@dataclass
class DeviceInfo:

    client_identifier: str

    device_model: str | None = None

    device_os: str | None = None

    os_version: str | None = None

    client_app: str | None = None

    client_version: str | None = None


class DeviceService:

    # ============================================================
    # DETECT CLIENT
    # ============================================================

    @staticmethod
    def _parse_user_agent(
        user_agent: str,
    ) -> tuple[
        str | None,
        str | None,
    ]:

        if not user_agent:
            return None, None

        first_part = (
            user_agent
            .split(" ", 1)[0]
        )

        if "/" not in first_part:
            return first_part, None

        parts = first_part.split("/")

        app = (
            parts[0]
            if len(parts) >= 1
            else None
        )

        version = (
            parts[1]
            if len(parts) >= 2
            else None
        )

        return app, version

    @staticmethod
    def _normalize_model(
        model: str | None,
    ) -> str | None:

        if not model:
            return None

        model = model.strip()

        # TECNO TECNO LJ7 -> TECNO LJ7
        parts = model.split()

        if (
            len(parts) >= 2
            and parts[0].lower()
            == parts[1].lower()
        ):
            parts.pop(0)

        return " ".join(parts)

    def detect(
        self,
        request: Request,
    ) -> DeviceInfo | None:

        headers = request.headers

        # Наш будущий клиент:
        # X-Device-Id
        #
        # Happ / INCY:
        # X-Hwid
        client_identifier = (
            headers.get("x-device-id")
            or headers.get("x-hwid")
        )

        if not client_identifier:
            return None

        user_agent = (
            headers.get("user-agent")
            or ""
        )

        client_app = headers.get(
            "x-client-app"
        )

        client_version = headers.get(
            "x-client-version"
        )

        detected_app, detected_version = (
            self._parse_user_agent(
                user_agent
            )
        )

        if not client_app:
            client_app = detected_app

        if not client_version:
            client_version = detected_version

        return DeviceInfo(
            client_identifier=(
                client_identifier
            ),
            device_model=(
                self._normalize_model(
                    headers.get(
                        "x-device-model"
                    )
                )
            ),
            device_os=headers.get(
                "x-device-os"
            ),
            os_version=headers.get(
                "x-ver-os"
            ),
            client_app=client_app,
            client_version=client_version,
        )

    # ============================================================
    # REGISTER CLIENT ON DEVICE
    # ============================================================

    def register(
        self,
        subscription,
        device_info: DeviceInfo,
        device_token: str | None = None,
    ):

        # --------------------------------------------------------
        # 1. Этот конкретный client identifier уже известен.
        #
        # Например INCY повторно обновляет подписку.
        # --------------------------------------------------------

        existing_device = (
            device_repo.get_by_client_identifier(
                subscription.id,
                device_info.client_identifier,
            )
        )

        if existing_device is not None:

            if not existing_device.is_active:

                raise HTTPException(
                    status_code=403,
                    detail="Device is disabled",
                )

            device_repo.touch(
                existing_device.id,
                device_name=(
                    device_info.device_model
                ),
                device_model=(
                    device_info.device_model
                ),
                device_os=(
                    device_info.device_os
                ),
                os_version=(
                    device_info.os_version
                ),
            )

            device_repo.add_or_update_client(
                device_id=existing_device.id,
                client_identifier=(
                    device_info.client_identifier
                ),
                client_app=(
                    device_info.client_app
                ),
                client_version=(
                    device_info.client_version
                ),
            )

            logger.info(
                "Known device client updated: "
                "subscription_id={} "
                "device_id={} "
                "app={}",
                subscription.id,
                existing_device.id,
                device_info.client_app,
            )

            return device_repo.get_by_id(
                existing_device.id
            )

        # --------------------------------------------------------
        # 2. Нам передали device_token.
        #
        # Это новый клиент/app, который нужно привязать
        # к уже существующему физическому устройству.
        # --------------------------------------------------------

        if device_token:

            device = device_repo.get_by_token(
                device_token
            )

            if device is None:

                raise HTTPException(
                    status_code=404,
                    detail="Device not found",
                )

            if (
                device.subscription_id
                != subscription.id
            ):

                raise HTTPException(
                    status_code=403,
                    detail="Device does not belong to subscription",
                )

            if not device.is_active:

                raise HTTPException(
                    status_code=403,
                    detail="Device is disabled",
                )

            device_repo.touch(
                device.id,
                device_name=(
                    device_info.device_model
                ),
                device_model=(
                    device_info.device_model
                ),
                device_os=(
                    device_info.device_os
                ),
                os_version=(
                    device_info.os_version
                ),
            )

            device_repo.add_or_update_client(
                device_id=device.id,
                client_identifier=(
                    device_info.client_identifier
                ),
                client_app=(
                    device_info.client_app
                ),
                client_version=(
                    device_info.client_version
                ),
            )

            logger.info(
                "New client linked to device: "
                "subscription_id={} "
                "device_id={} "
                "app={}",
                subscription.id,
                device.id,
                device_info.client_app,
            )

            return device_repo.get_by_id(
                device.id
            )

        # --------------------------------------------------------
        # 3. Совершенно новая подписка.
        #
        # Если физических устройств ещё вообще нет,
        # первый импорт автоматически создаёт Device #1.
        # --------------------------------------------------------

        active_devices = (
            device_repo.get_by_subscription(
                subscription.id,
                active_only=True,
            )
        )

        if not active_devices:

            if subscription.device_limit < 1:

                raise HTTPException(
                    status_code=403,
                    detail="Device limit reached",
                )

            device = device_repo.create(
                subscription_id=subscription.id,
                device_name=(
                    device_info.device_model
                ),
                device_model=(
                    device_info.device_model
                ),
                device_os=(
                    device_info.device_os
                ),
                os_version=(
                    device_info.os_version
                ),
            )

            device_repo.add_or_update_client(
                device_id=device.id,
                client_identifier=(
                    device_info.client_identifier
                ),
                client_app=(
                    device_info.client_app
                ),
                client_version=(
                    device_info.client_version
                ),
            )

            logger.info(
                "First physical device created: "
                "subscription_id={} "
                "device_id={} "
                "model={} "
                "app={}",
                subscription.id,
                device.id,
                device.device_model,
                device_info.client_app,
            )

            return device

        # --------------------------------------------------------
        # 4. Устройства уже существуют, но пришёл совершенно
        # новый HWID без device_token.
        #
        # НЕ пытаемся угадывать по модели телефона.
        #
        # Это защищает нас от ситуации:
        # два одинаковых TECNO/Pixel/iPhone ошибочно склеились.
        # --------------------------------------------------------

        logger.warning(
            "Unknown client without device token: "
            "subscription_id={} "
            "model={} "
            "app={}",
            subscription.id,
            device_info.device_model,
            device_info.client_app,
        )

        raise HTTPException(
            status_code=409,
            detail=(
                "Use device-specific subscription link"
            ),
        )


device_service = DeviceService()

from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import uuid4

from loguru import logger

from app.config import settings
from app.domain.inbound import Inbound
from app.domain.legacy_enums import SubscriptionStatus
from app.domain.subscription import Subscription
from app.protocols.handlers.base import ProtocolHandler
from app.utils.client_email import generate_client_email


class VLESSHandler(ProtocolHandler):
    """
    VLESS Reality protocol handler.

    Вся специфическая логика VLESS находится здесь.

    VPNService не должен знать:
        - как создаётся VLESS client;
        - как строится VLESS URI;
        - как работает Reality;
        - как получать subscription link;
        - как восстанавливать VLESS клиента.

    Всё это находится внутри этого handler.
    """

    protocol = "vless"
    def __init__(
        self,
        server=None,
    ):
        self.server = server

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _random_string(
        length: int = 16,
    ) -> str:
        """
        Генерирует случайную строку.

        Используется для дополнительных полей,
        которые ожидает API 3x-ui.
        """

        alphabet = (
            string.ascii_lowercase
            + string.digits
        )

        return "".join(
            secrets.choice(alphabet)
            for _ in range(length)
        )

    @staticmethod
    def _expiry_timestamp(
        expires_at: datetime,
    ) -> int:
        """
        datetime -> Unix timestamp milliseconds.
        """

        return int(
            expires_at.timestamp() * 1000
        )

    # ============================================================
    # INBOUND
    # ============================================================

    async def get_inbound(
        self,
        xui,
    ) -> Inbound | None:
        """
        Получает VLESS inbound из 3x-ui.
        """

        inbound = await xui.get_default_inbound(
            self.protocol
        )

        if inbound is None:
            logger.warning(
                "VLESS inbound not found"
            )
            return None

        logger.info(
            "VLESS inbound found: "
            "id={} remark={} protocol={} port={}",
            inbound.id,
            inbound.remark,
            inbound.protocol,
            inbound.port,
        )

        return inbound

    async def get_inbound_for_subscription(
        self,
        xui,
        subscription: Subscription,
    ) -> Inbound:
        """
        Получает конкретный inbound подписки.

        В первую очередь используем inbound_id,
        сохранённый в Subscription.

        Это важно, если на сервере несколько VLESS inbound.
        """

        inbound = await xui.get_inbound_by_id(
            subscription.inbound_id
        )

        if inbound is None:
            raise RuntimeError(
                f"VLESS inbound "
                f"{subscription.inbound_id} not found."
            )

        return inbound

    # ============================================================
    # CLIENT PAYLOAD
    # ============================================================

    def build_payload(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> dict:
        """
        Формирует payload VLESS клиента для 3x-ui.
        """

        return {
            "id": subscription.client_id,
            "email": subscription.client_email,

            "password": self._random_string(16),
            "auth": self._random_string(16),

            "flow": "xtls-rprx-vision",
            "security": "auto",

            "limitIp": 0,
            "totalGB": 0,

            "expiryTime": self._expiry_timestamp(
                subscription.expires_at
            ),

            "tgId": 0,
            "reset": 0,
            "group": "",
            "comment": "",
            "enable": True,
        }

    # ============================================================
    # VLESS REALITY CONFIG
    # ============================================================

    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:
        """
        Строит VLESS Reality URI.
        """

        stream_settings = inbound.raw.get(
            "streamSettings",
            {},
        )

        reality = stream_settings.get(
            "realitySettings",
            {},
        )

        reality_settings = reality.get(
            "settings",
            {},
        )

        public_key = reality_settings.get(
            "publicKey"
        )

        target = reality.get(
            "target",
            ""
        )

        short_ids = reality.get(
            "shortIds",
            []
        )

        if not public_key:
            raise ValueError(
                "VLESS Reality publicKey not found"
            )

        if not target:
            raise ValueError(
                "VLESS Reality target not found"
            )

        if not short_ids:
            raise ValueError(
                "VLESS Reality shortIds not found"
            )

        sni = target.split(
            ":",
            1,
        )[0]

        params = urlencode(
            {
                "type": "tcp",
                "security": "reality",
                "pbk": public_key,
                "fp": "chrome",
                "sni": sni,
                "sid": short_ids[0],
                "spx": "/",
                "flow": "xtls-rprx-vision",
            }
        )

        return (
            f"vless://{subscription.client_id}"
            f"@{settings.vpn_host}:{inbound.port}"
            f"?{params}"
            f"#{settings.vpn_name}"
        )

    # ============================================================
    # CONFIG
    # ============================================================

    async def _get_config(
        self,
        xui,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:
        """
        Получает subscription link из 3x-ui.

        Если 3x-ui не вернул ссылку,
        строим обычный VLESS Reality URI самостоятельно.
        """

        if subscription.sub_id:
            links = await xui.get_subscription_links(
                subscription.sub_id,
            )

            if links:
                return links[0]

        return self.build_config(
            subscription,
            inbound,
        )

    # ============================================================
    # CREATE
    # ============================================================

    async def create_subscription(
        self,
        xui,
        server,
        user_id: int,
        days: int,
    ) -> Subscription:
        """
        Создаёт VLESS подписку.

        Контракт общий для всех VPN-протоколов:

            xui
            server
            user_id
            days
        """

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'vless' не найден"
            )

        now = datetime.now()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            server_id=server.id,
            protocol=self.protocol,
            inbound_id=inbound.id,
            client_id=str(uuid4()),
            client_email=generate_client_email(
                user_id
            ),
            sub_id=str(uuid4()),
            config="",
            status=SubscriptionStatus.ACTIVE,
            created_at=now,
            expires_at=(
                now
                + timedelta(days=days)
            ),
        )

        logger.info(
            "Creating VLESS client: "
            "user_id={} client_id={} "
            "server_id={} inbound_id={}",
            user_id,
            subscription.client_id,
            server.id,
            inbound.id,
        )

        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )

        updated_inbound = await xui.refresh_inbound(
            inbound
        )

        if updated_inbound is None:
            raise RuntimeError(
                "Не удалось обновить VLESS inbound."
            )

        client = await xui.get_client(
            updated_inbound,
            subscription.client_id,
        )

        if client is None:
            raise RuntimeError(
                "VLESS клиент после создания "
                "не найден в 3x-ui."
            )

        subscription.sub_id = client.get(
            "subId",
            subscription.sub_id,
        )

        subscription.config = await self._get_config(
            xui=xui,
            subscription=subscription,
            inbound=updated_inbound,
        )

        logger.info(
            "VLESS subscription created: "
            "client_id={} sub_id={}",
            subscription.client_id,
            subscription.sub_id,
        )

        return subscription

    # ============================================================
    # RENEW
    # ============================================================

    async def renew(
        self,
        xui,
        subscription: Subscription,
        days: int,
    ) -> Subscription:
        """
        Продлевает VLESS подписку.
        """

        now = datetime.now()

        expires = (
            max(
                now,
                subscription.expires_at,
            )
            + timedelta(days=days)
        )

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        updated = await xui.update_client(
            inbound=inbound,
            client_uuid=subscription.client_id,
            expiry_time=self._expiry_timestamp(
                expires
            ),
            enable=True,
        )

        if not updated:
            logger.warning(
                "VLESS client not found during renew: "
                "client_id={}",
                subscription.client_id,
            )

            subscription.expires_at = expires

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        subscription.expires_at = expires

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        subscription.config = await self._get_config(
            xui=xui,
            subscription=subscription,
            inbound=inbound,
        )

        logger.info(
            "VLESS subscription renewed: "
            "client_id={} expires_at={}",
            subscription.client_id,
            subscription.expires_at,
        )

        return subscription

    # ============================================================
    # DISABLE
    # ============================================================

    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Отключает VLESS клиента.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        await xui.set_client_enabled(
            inbound=inbound,
            client_uuid=subscription.client_id,
            enabled=False,
        )

        subscription.status = (
            SubscriptionStatus.DISABLED
        )

        logger.info(
            "VLESS client disabled: "
            "client_id={}",
            subscription.client_id,
        )

        return subscription

    # ============================================================
    # RESTORE
    # ============================================================

    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Восстанавливает VLESS клиента,
        если он отсутствует в 3x-ui.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        logger.warning(
            "Restoring VLESS client: "
            "client_id={} email={}",
            subscription.client_id,
            subscription.client_email,
        )

        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )

        updated_inbound = await xui.refresh_inbound(
            inbound
        )

        if updated_inbound is None:
            raise RuntimeError(
                "Не удалось обновить VLESS inbound "
                "после восстановления."
            )

        client = await xui.get_client(
            updated_inbound,
            subscription.client_id,
        )

        if client is None:
            raise RuntimeError(
                "VLESS клиент после восстановления "
                "не найден."
            )

        subscription.sub_id = client.get(
            "subId",
            subscription.sub_id,
        )

        subscription.config = await self._get_config(
            xui=xui,
            subscription=subscription,
            inbound=updated_inbound,
        )

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        logger.info(
            "VLESS client restored: "
            "client_id={} sub_id={}",
            subscription.client_id,
            subscription.sub_id,
        )

        return subscription

    # ============================================================
    # SYNC
    # ============================================================

    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Синхронизирует локальную подписку
        с клиентом в 3x-ui.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        inbound = await xui.refresh_inbound(
            inbound
        )

        if inbound is None:
            raise RuntimeError(
                "Не удалось обновить VLESS inbound."
            )

        client = await xui.get_client(
            inbound,
            subscription.client_id,
        )

        # --------------------------------------------------------
        # Клиент отсутствует
        # --------------------------------------------------------

        if client is None:
            logger.warning(
                "VLESS client missing during sync: "
                "client_id={}",
                subscription.client_id,
            )

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        # --------------------------------------------------------
        # subId
        # --------------------------------------------------------

        subscription.sub_id = client.get(
            "subId",
            subscription.sub_id,
        )

        # --------------------------------------------------------
        # Expiry
        # --------------------------------------------------------

        expiry = client.get(
            "expiryTime",
            0,
        )

        if expiry:
            subscription.expires_at = (
                datetime.fromtimestamp(
                    expiry / 1000
                )
            )

        # --------------------------------------------------------
        # Status
        # --------------------------------------------------------

        subscription.status = (
            SubscriptionStatus.ACTIVE
            if client.get(
                "enable",
                True,
            )
            else SubscriptionStatus.DISABLED
        )

        # --------------------------------------------------------
        # Config
        # --------------------------------------------------------

        subscription.config = await self._get_config(
            xui=xui,
            subscription=subscription,
            inbound=inbound,
        )

        logger.debug(
            "VLESS sync complete: "
            "subscription={} client_id={} "
            "status={} expires_at={}",
            subscription.id,
            subscription.client_id,
            subscription.status,
            subscription.expires_at,
        )

        return subscription

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        xui,
        subscription: Subscription,
    ) -> None:
        """
        Удаляет VLESS клиента из 3x-ui.
        """

        await xui.delete_client(
            subscription.client_email,
        )

        logger.info(
            "VLESS client deleted: "
            "client_id={}",
            subscription.client_id,
        )

    # ============================================================
    # FILE
    # ============================================================

    async def get_file(
        self,
        xui,
        subscription: Subscription,
    ) -> tuple[str, bytes]:
        """
        Возвращает VLESS конфигурацию
        в виде текстового файла.
        """

        if not subscription.config:
            inbound = await self.get_inbound_for_subscription(
                xui,
                subscription,
            )

            subscription.config = self.build_config(
                subscription,
                inbound,
            )

        filename = (
            subscription.client_email
            if subscription.client_email.endswith(".txt")
            else f"{subscription.client_email}.txt"
        )

        return (
            filename,
            subscription.config.encode(
                "utf-8"
            ),
        )

    # ============================================================
    # RESTORE ALIAS
    # ============================================================

    async def restore(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Общий метод восстановления,
        предусмотренный ProtocolHandler.
        """

        return await self.restore_client(
            xui=xui,
            subscription=subscription,
        )


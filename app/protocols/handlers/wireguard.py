
from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from loguru import logger

from app.domain.inbound import Inbound
from app.domain.legacy_enums import SubscriptionStatus
from app.domain.subscription import Subscription
from app.protocols.handlers.base import ProtocolHandler
from app.utils.client_email import generate_client_email


class WireGuardHandler(ProtocolHandler):
    """
    WireGuard protocol handler.

    WireGuard остаётся поддерживаемым протоколом,
    но не является обязательным или основным протоколом системы.

    Вся специфическая работа с WireGuard находится здесь.
    """

    protocol = "wireguard"

    def __init__(
        self,
        server=None,
    ):
        self.server = server

    # ------------------------------------------------------------------
    # Inbound
    # ------------------------------------------------------------------

    async def get_inbound(
        self,
        xui,
    ) -> Inbound | None:
        """
        Получает WireGuard inbound.
        """

        return await xui.get_inbound(
            self.protocol
        )

    async def get_inbound_for_subscription(
        self,
        xui,
        subscription: Subscription,
    ) -> Inbound:
        """
        Получает inbound, к которому привязана подписка.
        """

        inbound = await xui.get_inbound_by_id(
            subscription.inbound_id
        )

        if inbound is None:
            raise RuntimeError(
                f"Inbound {subscription.inbound_id} not found."
            )

        return inbound

    # ------------------------------------------------------------------
    # Payload
    # ------------------------------------------------------------------

    def build_payload(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> dict:
        """
        Формирует payload клиента WireGuard для 3x-ui.
        """

        return {
            "id": subscription.client_id,
            "email": subscription.client_email,
            "enable": True,
            "expiryTime": int(
                subscription.expires_at.timestamp()
                * 1000
            ),
        }

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:
        """
        Для WireGuard конфигурация генерируется самим XUI.
        """

        return subscription.config

    # ------------------------------------------------------------------
    # Create subscription
    # ------------------------------------------------------------------

    async def create_subscription(
        self,
        xui,
        server,
        user_id: int,
        days: int,
    ) -> Subscription:
        """
        Создаёт WireGuard клиента
        и локальную Subscription.
        """

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise RuntimeError(
                "WireGuard inbound not found."
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

            config="",

            status=SubscriptionStatus.ACTIVE,

            created_at=now,

            expires_at=(
                now
                + timedelta(days=days)
            ),
        )

        logger.info(
            "Creating WireGuard client: "
            "user_id={} client_id={} email={} inbound_id={}",
            user_id,
            subscription.client_id,
            subscription.client_email,
            inbound.id,
        )

        # --------------------------------------------------------------
        # Создаём клиента
        # --------------------------------------------------------------

        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )

        # --------------------------------------------------------------
        # Обновляем inbound
        # --------------------------------------------------------------

        updated = await xui.refresh_inbound(
            inbound
        )

        if updated is None:
            raise RuntimeError(
                "Не удалось обновить inbound "
                "после создания WireGuard клиента."
            )

        # --------------------------------------------------------------
        # Проверяем клиента
        # --------------------------------------------------------------

        client = await xui.get_wireguard_client(
            updated,
            subscription.client_email,
        )

        if client is None:
            raise RuntimeError(
                "WireGuard client was not created in XUI."
            )

        # --------------------------------------------------------------
        # Сохраняем фактический ID XUI
        # --------------------------------------------------------------

        subscription.client_id = client.get(
            "id",
            subscription.client_id,
        )

        # --------------------------------------------------------------
        # Получаем конфигурацию
        # --------------------------------------------------------------

        subscription.config = (
            await xui.get_wireguard_config(
                updated,
                subscription.client_email,
            )
        )

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        logger.info(
            "WireGuard subscription created: "
            "client_id={} email={}",
            subscription.client_id,
            subscription.client_email,
        )

        return subscription

    # ------------------------------------------------------------------
    # Renew
    # ------------------------------------------------------------------

    async def renew(
        self,
        xui,
        subscription: Subscription,
        days: int,
    ) -> Subscription:
        """
        Продлевает WireGuard подписку.
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
            email=subscription.client_email,
            expiry_time=int(
                expires.timestamp()
                * 1000
            ),
            enable=True,
        )

        if not updated:
            logger.warning(
                "WireGuard client not found during renew: "
                "client_id={} email={}",
                subscription.client_id,
                subscription.client_email,
            )

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        subscription.expires_at = expires

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        subscription.config = (
            await xui.get_wireguard_config(
                inbound,
                subscription.client_email,
            )
        )

        logger.info(
            "WireGuard subscription renewed: "
            "client_id={} expires_at={}",
            subscription.client_id,
            subscription.expires_at,
        )

        return subscription

    # ------------------------------------------------------------------
    # Disable
    # ------------------------------------------------------------------

    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Отключает WireGuard клиента.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        await xui.set_client_enabled(
            inbound=inbound,
            client_uuid=subscription.client_id,
            email=subscription.client_email,
            enabled=False,
        )

        subscription.status = (
            SubscriptionStatus.DISABLED
        )

        logger.info(
            "WireGuard client disabled: "
            "client_id={} email={}",
            subscription.client_id,
            subscription.client_email,
        )

        return subscription

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------

    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Восстанавливает WireGuard клиента.

        Если клиент уже существует —
        просто включаем и обновляем его.

        Если клиента нет —
        создаём заново.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        # --------------------------------------------------------------
        # Проверяем существующего клиента
        # --------------------------------------------------------------

        existing = await xui.get_wireguard_client(
            inbound,
            subscription.client_email,
        )

        if existing:
            logger.info(
                "WireGuard client already exists. "
                "Restoring: email={}",
                subscription.client_email,
            )

            actual_client_id = existing.get(
                "id"
            )

            if actual_client_id:
                subscription.client_id = (
                    actual_client_id
                )

            # Включаем клиента.
            await xui.set_client_enabled(
                inbound=inbound,
                client_uuid=subscription.client_id,
                email=subscription.client_email,
                enabled=True,
            )

            # Обновляем expiry.
            await xui.update_client(
                inbound=inbound,
                client_uuid=subscription.client_id,
                email=subscription.client_email,
                expiry_time=int(
                    subscription.expires_at.timestamp()
                    * 1000
                ),
                enable=True,
            )

            subscription.config = (
                await xui.get_wireguard_config(
                    inbound,
                    subscription.client_email,
                )
            )

            subscription.status = (
                SubscriptionStatus.ACTIVE
            )

            return subscription

        # --------------------------------------------------------------
        # Клиента нет — создаём заново
        # --------------------------------------------------------------

        logger.warning(
            "WireGuard client missing. "
            "Creating new client: email={}",
            subscription.client_email,
        )

        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )

        updated = await xui.refresh_inbound(
            inbound
        )

        if updated is None:
            raise RuntimeError(
                "Не удалось обновить inbound "
                "после восстановления WireGuard клиента."
            )

        restored_client = (
            await xui.get_wireguard_client(
                updated,
                subscription.client_email,
            )
        )

        if restored_client is None:
            raise RuntimeError(
                "WireGuard client restore failed."
            )

        actual_client_id = restored_client.get(
            "id"
        )

        if actual_client_id:
            subscription.client_id = (
                actual_client_id
            )

        subscription.config = (
            await xui.get_wireguard_config(
                updated,
                subscription.client_email,
            )
        )

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        logger.info(
            "WireGuard client restored: "
            "client_id={} email={}",
            subscription.client_id,
            subscription.client_email,
        )

        return subscription

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:
        """
        Синхронизирует WireGuard клиента
        с состоянием в 3x-ui.
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
                "Inbound refresh failed."
            )

        # --------------------------------------------------------------
        # Ищем клиента
        # --------------------------------------------------------------

        client = await xui.get_wireguard_client(
            inbound,
            subscription.client_email,
        )

        # --------------------------------------------------------------
        # Клиента нет → восстанавливаем
        # --------------------------------------------------------------

        if client is None:
            logger.warning(
                "WireGuard client missing in XUI. "
                "Restoring: email={}",
                subscription.client_email,
            )

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        # --------------------------------------------------------------
        # Обновляем client_id
        # --------------------------------------------------------------

        actual_client_id = client.get(
            "id"
        )

        if actual_client_id:
            subscription.client_id = (
                actual_client_id
            )

        # --------------------------------------------------------------
        # Обновляем expiry
        # --------------------------------------------------------------

        expiry = client.get(
            "expiryTime"
        )

        if expiry:
            subscription.expires_at = (
                datetime.fromtimestamp(
                    expiry / 1000
                )
            )

        # --------------------------------------------------------------
        # Обновляем статус
        # --------------------------------------------------------------

        subscription.status = (
            SubscriptionStatus.ACTIVE
            if client.get(
                "enable",
                True,
            )
            else SubscriptionStatus.DISABLED
        )

        # --------------------------------------------------------------
        # Получаем свежий конфиг
        # --------------------------------------------------------------

        subscription.config = (
            await xui.get_wireguard_config(
                inbound,
                subscription.client_email,
            )
        )

        # --------------------------------------------------------------
        # Если клиент выключен,
        # но подписка ещё действительна —
        # восстанавливаем.
        # --------------------------------------------------------------

        if (
            subscription.status
            == SubscriptionStatus.DISABLED
            and subscription.expires_at > datetime.now()
        ):
            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        return subscription

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete(
        self,
        xui,
        subscription: Subscription,
    ) -> None:
        """
        Удаляет WireGuard клиента.

        В текущей реализации удаление выполняется
        через disable, чтобы не потерять конфигурацию
        и состояние подписки.
        """

        await self.disable(
            xui=xui,
            subscription=subscription,
        )

    # ------------------------------------------------------------------
    # Config file
    # ------------------------------------------------------------------

    async def get_file(
        self,
        xui,
        subscription: Subscription,
    ) -> tuple[str, bytes]:
        """
        Возвращает WireGuard .conf файл.
        """

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        config = await xui.get_wireguard_config(
            inbound,
            subscription.client_email,
        )

        return (
            f"{subscription.client_email}.conf",
            config.encode("utf-8"),
        )


    async def restore(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

        return await self.restore_client(
            xui=xui,
            subscription=subscription,
        )

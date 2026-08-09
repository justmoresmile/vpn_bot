from loguru import logger

from app.domain.subscription import Subscription
from app.domain.legacy_enums import SubscriptionStatus
from app.protocols.handlers.base import ProtocolHandler
from app.repositories.subscription_repository import subscription_repo
from app.repositories.subscription_notification_repository import (
    subscription_notification_repo,
)
from app.services.server_service import server_service
from app.services.xui_client import XUIClient
from app.services.subscription_token import (
    generate_subscription_token,
)

class VPNService:

    def __init__(self):
        self._xui_clients: dict[int, XUIClient] = {}

    # ============================================================
    # SERVER
    # ============================================================

    @staticmethod
    def _get_server(
        subscription: Subscription,
    ):
        server = server_service.get_by_id(
            subscription.server_id
        )

        if server is None:
            raise RuntimeError(
                f"Server {subscription.server_id} not found."
            )

        return server

    # ============================================================
    # XUI
    # ============================================================

    async def _get_xui(
        self,
        server,
    ) -> XUIClient:

        if server.id not in self._xui_clients:
            self._xui_clients[server.id] = XUIClient(
                server
            )

        return self._xui_clients[server.id]

    # ============================================================
    # PROTOCOL
    # ============================================================

    @staticmethod
    def _get_handler(
        subscription: Subscription,
    ) -> ProtocolHandler:

        server = VPNService._get_server(
            subscription
        )

        return ProtocolHandler.create(
            protocol=subscription.protocol,
            server=server,
        )

    @staticmethod
    def get_protocols() -> list[str]:
        """
        Возвращает все зарегистрированные протоколы.

        Например:

            [
                "vless",
                "wireguard",
            ]
        """

        return ProtocolHandler.protocols()

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        protocol = protocol.lower().strip()

        if protocol not in ProtocolHandler.protocols():
            raise ValueError(
                f"Unsupported VPN protocol: {protocol}"
            )

        server = server_service.get_best_server()

        if server is None:
            raise RuntimeError(
                "No available VPN server found."
            )

        handler = ProtocolHandler.create(
            protocol=protocol,
            server=server,
        )

        xui = await self._get_xui(
            server
        )

        subscription = await handler.create_subscription(
            xui=xui,
            server=server,
            user_id=user_id,
            days=days,
        )

        subscription.server_id = server.id
        subscription.protocol = protocol

        subscription.subscription_token = (
            generate_subscription_token()
        )

        created = subscription_repo.create(
            subscription
        )

        logger.info(
            "VPN subscription created "
            "user={} subscription={} "
            "server={} protocol={}",
            user_id,
            created.id,
            server.id,
            protocol,
        )

        return created

    # ============================================================
    # PURCHASE
    # ============================================================

    async def purchase(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        protocol = protocol.lower().strip()

        if protocol not in ProtocolHandler.protocols():
            raise ValueError(
                f"Unsupported VPN protocol: {protocol}"
            )

        logger.info(
            "Creating new subscription "
            "user={} protocol={} days={}",
            user_id,
            protocol,
            days,
        )

        return await self.create(
            user_id=user_id,
            protocol=protocol,
            days=days,
        )

    # ============================================================
    # RENEW
    # ============================================================

    async def renew(
        self,
        subscription_id: int,
        days: int,
    ) -> Subscription:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            raise ValueError(
                "Подписка не найдена"
            )

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        renewed = await handler.renew(
            xui=xui,
            subscription=subscription,
            days=days,
        )

        subscription_repo.update(
            renewed
        )

        subscription_notification_repo.delete_by_subscription(
            renewed.id
        )

        logger.info(
            "Subscription {} renewed protocol={}",
            renewed.id,
            renewed.protocol,
        )

        return renewed

    # ============================================================
    # EXTEND
    # ============================================================

    async def extend(
        self,
        subscription_id: int,
        days: int,
    ) -> Subscription:

        subscription = await self.renew(
            subscription_id,
            days,
        )

        subscription_notification_repo.delete_by_subscription(
            subscription.id
        )

        logger.info(
            "Notifications reset for subscription {}",
            subscription.id,
        )

        return subscription

    # ============================================================
    # DISABLE
    # ============================================================

    async def disable(
        self,
        subscription: Subscription,
    ) -> Subscription:

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        disabled = await handler.disable(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.update(
            disabled
        )

        logger.warning(
            "Subscription {} disabled protocol={}",
            disabled.id,
            disabled.protocol,
        )

        return disabled

    # ============================================================
    # DISABLE BY ID
    # ============================================================

    async def disable_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        return await self.disable(
            subscription
        )

    # ============================================================
    # GET CONFIG
    # ============================================================

    async def get_config(
        self,
        subscription_id: int,
    ) -> str | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        return subscription.config

    # ============================================================
    # GET FILE
    # ============================================================

    async def get_file(
        self,
        subscription: Subscription,
    ) -> tuple[str, bytes]:

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        return await handler.get_file(
            xui=xui,
            subscription=subscription,
        )

    # ============================================================
    # GET USER SUBSCRIPTIONS
    # ============================================================

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Subscription]:

        return subscription_repo.get_by_user(
            user_id
        )

    # ============================================================
    # GET SUBSCRIPTION
    # ============================================================

    async def get_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        synced = await handler.sync(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.update(
            synced
        )

        return synced

    # ============================================================
    # SYNC
    # ============================================================

    async def sync_subscription(
        self,
        subscription: Subscription,
    ) -> Subscription:

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        synced = await handler.sync(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.update(
            synced
        )

        return synced

    # ============================================================
    # RESTORE
    # ============================================================

    async def restore_client(
        self,
        subscription: Subscription,
    ) -> Subscription:

        if (
            subscription.status
            == SubscriptionStatus.EXPIRED
        ):
            raise ValueError(
                "Подписка истекла"
            )

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        restored = await handler.restore(
            xui=xui,
            subscription=subscription,
        )

        subscription_repo.update(
            restored
        )

        logger.info(
            "Subscription {} restored protocol={}",
            restored.id,
            restored.protocol,
        )

        return restored

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        subscription: Subscription,
    ) -> None:

        server = self._get_server(
            subscription
        )

        handler = self._get_handler(
            subscription
        )

        xui = await self._get_xui(
            server
        )

        await handler.delete(
            xui=xui,
            subscription=subscription,
        )

        logger.info(
            "Subscription {} deleted protocol={}",
            subscription.id,
            subscription.protocol,
        )

    # ============================================================
    # CLOSE XUI CLIENTS
    # ============================================================

    async def close(self):

        for xui in self._xui_clients.values():
            await xui.close()

        self._xui_clients.clear()

        logger.info(
            "XUI clients closed"
        )


vpn_service = VPNService()
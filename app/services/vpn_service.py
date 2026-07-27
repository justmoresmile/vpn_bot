from loguru import logger

from app.domain.subscription import Subscription
from app.domain.legacy_enums import SubscriptionStatus
from app.protocols.handlers.base import ProtocolHandler
from app.repositories.subscription_repository import subscription_repo
from app.services.xui_client import XUIClient
from app.services.server_service import server_service
from app.repositories.subscription_notification_repository import (
    subscription_notification_repo,
)
from app.repositories.user_repository import users_repo

from app.bot.services.telegram_service import telegram_service

class VPNService:


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

   

    async def create(
        self,
        user_id: int,
        protocol: str = "wireguard",
        days: int = 30,
    ) -> Subscription:

        server = server_service.get_best_server()

        handler = ProtocolHandler.create(
            protocol
        )

        async with XUIClient(server) as xui:

            subscription = await handler.create_subscription(
                xui=xui,
                user_id=user_id,
                server=server,
                days=days,
            )

        subscription.server_id = server.id

        created = subscription_repo.create(
            subscription
        )

        logger.info(
            "VPN created user={} subscription={} server={}",
            user_id,
            created.id,
            server.id,
        )

        return created

   
    async def purchase(
        self,
        user_id: int,
        protocol: str = "wireguard",
        days: int = 30,
    ) -> Subscription:


        subscription = (
            subscription_repo
            .get_active_by_user_protocol(
                user_id,
                protocol,
            )
        )


        if subscription is not None:

            return await self.renew(
                subscription.id,
                days,
            )


        return await self.create(
            user_id=user_id,
            protocol=protocol,
            days=days,
        )


    
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


        old_expires_at = subscription.expires_at
        server = self._get_server(
            subscription
        )

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            renewed = await handler.renew(
                xui=xui,
                subscription=subscription,
                days=days,
            )


        subscription_repo.update(
            renewed
        )


        user = users_repo.get_by_id(
            renewed.user_id
        )


        if user and old_expires_at:

            await telegram_service.send_renew_notification(
                user.telegram_id,
                old_date=(
                    old_expires_at.strftime(
                        "%d.%m.%Y %H:%M"
                    )
                ),
                new_date=(
                    renewed.expires_at.strftime(
                        "%d.%m.%Y %H:%M"
                    )
                ),
            )


        logger.info(
            "Subscription {} renewed",
            renewed.id,
        )


        return renewed



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


    async def disable(
        self,
        subscription: Subscription,
    ) -> Subscription:

        server = self._get_server(
            subscription
        )

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

      

            disabled = await handler.disable(
                xui=xui,
                subscription=subscription,
            )

        subscription_repo.update(
            disabled
        )

        logger.warning(
            "Subscription {} disabled",
            disabled.id,
        )

        return disabled




    async def delete(
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

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            disabled = await handler.disable(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.update(
            disabled
        )


        logger.warning(
            "Subscription {} disabled",
            disabled.id,
        )


        return disabled







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

    async def get_file(
        self,
        subscription: Subscription,
    ) -> tuple[str, bytes]:

        server = self._get_server(
            subscription
        )

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            return await handler.get_file(
                xui,
                subscription,
            )


    def get_by_user(
        self,
        user_id: int,
    ) -> list[Subscription]:

        return subscription_repo.get_by_user(
            user_id
        )



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

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            synced = await handler.sync(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.update(
            synced
        )


        return synced



    async def sync_subscription(
        self,
        subscription: Subscription,
    ) -> Subscription:


        server = self._get_server(
            subscription
        )

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            synced = await handler.sync(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.update(
            synced
        )


        return synced


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

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient(server) as xui:

            restored = await handler.restore(
                xui=xui,
                subscription=subscription,
            )

        subscription_repo.update(
            restored
        )

        logger.info(
            "Subscription {} restored",
            restored.id,
        )

        return restored


vpn_service = VPNService()
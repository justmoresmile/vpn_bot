from loguru import logger

from app.domain.subscription import Subscription
from app.protocols.handlers.base import ProtocolHandler
import app.protocols
from app.repositories.subscription_repository import subscription_repo
from app.services.xui_client import XUIClient
from app.protocols.wireguard.link_parser import wireguard_link_to_config



class VPNService:


    async def create(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        async with XUIClient() as xui:

            handler = ProtocolHandler.create(
                protocol
            )

            subscription = await handler.create_subscription(
                xui=xui,
                user_id=user_id,
                days=days,
            )

            created = subscription_repo.create(
                subscription
            )

            logger.info(
                "VPN created user={} subscription={}",
                user_id,
                created.id,
            )

            return created


    async def purchase(
        self,
        user_id: int,
        protocol: str = "vless",
        days: int = 30,
    ) -> Subscription:

        subscription = subscription_repo.get_active_by_user_protocol(
            user_id,
            protocol,
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



        handler = ProtocolHandler.create(
            subscription.protocol
        )



        async with XUIClient() as xui:


            renewed = await handler.renew(
                xui=xui,
                subscription=subscription,
                days=days,
            )


        subscription_repo.update(
            renewed
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

        return await self.renew(
            subscription_id,
            days,
        )



    async def disable(
        self,
        subscription_id: int,
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


        handler = ProtocolHandler.create(
            subscription.protocol
        )


        async with XUIClient() as xui:

            disabled = await handler.disable(
                xui=xui,
                subscription=subscription,
            )



        subscription_repo.update(
            disabled
        )


        logger.info(
            "Subscription {} disabled",
            disabled.id,
        )


        return disabled


    async def delete(
        self,
        subscription_id: int,
    ) -> None:  

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return


        handler = ProtocolHandler.create(
            subscription.protocol
        )


        async with XUIClient() as xui:

            await handler.delete(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.delete(
            subscription.id
        )


        logger.info(
            "Subscription {} deleted",
            subscription.id,
        )


    async def restore_client(
        self,
        subscription: Subscription,
    ) -> Subscription:


        handler = ProtocolHandler.create(
            subscription.protocol
        )


        async with XUIClient() as xui:


            restored = await handler.restore_client(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.update(
            restored
        )


        logger.warning(
            "Client {} restored",
            restored.client_id,
        )


        return restored





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

        subscription = subscription_repo.get_by_id(
            subscription_id
        )

        if subscription is None:
            return None

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient() as xui:

            synced = await handler.sync(
                xui=xui,
                subscription=subscription,
            )

        subscription_repo.update(
            synced
        )

        return synced



    async def get_config_file(
        self,
        subscription_id: int,
    ):

        subscription = subscription_repo.get_by_id(
            subscription_id
        )

        if subscription is None:
            return None

        handler = ProtocolHandler.create(
            subscription.protocol
        )

        async with XUIClient() as xui:

            return await handler.get_file(
                xui=xui,
                subscription=subscription,
            )


    async def sync_subscription(
        self,
        subscription: Subscription,
    ) -> Subscription:


        handler = ProtocolHandler.create(
            subscription.protocol
        )


        async with XUIClient() as xui:

            synced = await handler.sync(
                xui=xui,
                subscription=subscription,
            )


        subscription_repo.update(
            synced
        )


        return synced
   

    async def get_wireguard_config(
        self,
        subscription: Subscription,
    ) -> str:

        async with XUIClient() as xui:

            inbound = await xui.get_inbound_by_id(
                subscription.inbound_id
            )

            if inbound is None:
                raise RuntimeError(
                    "Inbound не найден"
                )

            client = await xui.get_wireguard_client(
                inbound,
                subscription.client_email,
            )

            if client is None:
                raise RuntimeError(
                    "Клиент WireGuard не найден"
                )

            links = await xui.get_subscription_links(
                client["subId"]
            )

            if not links:
                raise RuntimeError(
                    "3x-ui не вернул ссылку подписки"
                )

            return wireguard_link_to_config(
                links[0]
            )



vpn_service = VPNService()
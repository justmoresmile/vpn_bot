from datetime import datetime, timedelta
from uuid import uuid4

from app.domain.legacy_enums import SubscriptionStatus
from app.domain.inbound import Inbound
from app.domain.subscription import Subscription
from app.protocols.handlers.base import ProtocolHandler
from app.utils.client_email import generate_client_email


class WireGuardHandler(ProtocolHandler):

    protocol = "wireguard"

    async def get_inbound(
        self,
        xui,
    ) -> Inbound | None:

        return await xui.get_inbound(
            self.protocol
        )

    def build_payload(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> dict:

        return {
            "id": subscription.client_id,
            "email": subscription.client_email,
            "enable": True,
            "expiryTime": int(
                subscription.expires_at.timestamp() * 1000
            ),
        }

    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:

        return subscription.config

    async def create_subscription(
        self,
        xui,
        server,
        user_id: int,
        days: int,
    ) -> Subscription:

        inbound = await self.get_inbound(xui)

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
            expires_at=now + timedelta(
                days=days
            ),
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
                "Не удалось обновить inbound"
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

        return subscription

    async def renew(
        self,
        xui,
        subscription: Subscription,
        days: int,
    ) -> Subscription:

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
                expires.timestamp() * 1000
            ),
            enable=True,
        )

        if not updated:

            return await self.restore_client(
                xui,
                subscription,
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

        return subscription


    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

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

        return subscription

    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

        inbound = await self.get_inbound_for_subscription(
            xui,
            subscription,
        )

        

        existing = await xui.get_wireguard_client(
            inbound,
            subscription.client_email,
        )

        #
        # Клиент существует → включаем его
        #
        if existing:

            await xui.set_client_enabled(
                inbound=inbound,
                client_uuid=subscription.client_id,
                email=subscription.client_email,
                enabled=True,
            )

            await xui.update_client(
                inbound=inbound,
                client_uuid=subscription.client_id,
                email=subscription.client_email,
                expiry_time=int(
                    subscription.expires_at.timestamp() * 1000
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

        #
        # Клиента нет → создаём заново
        #
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
                "Не удалось обновить inbound"
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

        return subscription

    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

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

        client = await xui.get_wireguard_client(
            inbound,
            subscription.client_email,
        )

        #
        # Клиент отсутствует в панели
        #
        if client is None:

            if (
                subscription.status
                == SubscriptionStatus.ACTIVE
                and subscription.expires_at > datetime.now()
            ):
                return await self.restore_client(
                    xui,
                    subscription,
                )

            return subscription

        #
        # Синхронизация срока действия
        #
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

        #
        # Синхронизация статуса
        #
        subscription.status = (
            SubscriptionStatus.ACTIVE
            if client.get(
                "enable",
                True,
            )
            else SubscriptionStatus.DISABLED
        )

        subscription.config = (
            await xui.get_wireguard_config(
                inbound,
                subscription.client_email,
            )
        )

        #
        # Если клиент отключён,
        # но подписка ещё действительна —
        # автоматически включаем.
        #
        if (
            subscription.status
            == SubscriptionStatus.DISABLED
            and subscription.expires_at > datetime.now()
        ):
            return await self.restore_client(
                xui,
                subscription,
            )

        return subscription

    async def delete(
        self,
        subscription: Subscription,
        xui,
    ) -> None:

        await self.disable(
            xui=xui,
            subscription=subscription,
        )


    async def get_file(
        self,
        xui,
        subscription: Subscription,
    ) -> tuple[str, bytes]:

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


    async def get_inbound_for_subscription(
        self,
        xui,
        subscription: Subscription,
    ) -> Inbound:

        inbound = await xui.get_inbound_by_id(
            subscription.inbound_id
        )

        if inbound is None:
            raise RuntimeError(
                f"Inbound {subscription.inbound_id} not found."
            )

        return inbound
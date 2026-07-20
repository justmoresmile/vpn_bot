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
        user_id: int,
        days: int,
    ) -> Subscription:

        inbound = await self.get_inbound(xui)

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
            )

        now = datetime.now()

        subscription = Subscription(
            id=None,
            user_id=user_id,
            protocol=self.protocol,
            inbound_id=inbound.id,
            client_id=str(uuid4()),
            client_email=generate_client_email(user_id),
            config="",
            status=SubscriptionStatus.ACTIVE,
            created_at=now,
            expires_at=now + timedelta(days=days),
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

        subscription.config = await xui.get_wireguard_config(
            updated,
            subscription.client_email,
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

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
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
        subscription.status = SubscriptionStatus.ACTIVE

        return subscription

    async def disable(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
            )

        await xui.set_client_enabled(
            inbound=inbound,
            client_uuid=subscription.client_id,
            email=subscription.client_email,
            enabled=False,
        )

        subscription.status = SubscriptionStatus.DISABLED

        return subscription

    async def restore_client(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
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

        subscription.config = await xui.get_wireguard_config(
            updated,
            subscription.client_email,
        )

        subscription.status = SubscriptionStatus.ACTIVE

        return subscription

    async def sync(
        self,
        xui,
        subscription: Subscription,
    ) -> Subscription:

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
            )

        inbound = await xui.refresh_inbound(
            inbound
        )

        if inbound is None:
            raise RuntimeError(
                "Не удалось обновить inbound"
            )

        client = await xui.get_wireguard_client(
            inbound,
            subscription.client_email,
        )

        if client is None:

            return await self.restore_client(
                xui,
                subscription,
            )

        expiry = client.get(
            "expiryTime",
            0,
        )

        if expiry:

            subscription.expires_at = datetime.fromtimestamp(
                expiry / 1000
            )

        subscription.status = (
            SubscriptionStatus.ACTIVE
            if client.get(
                "enable",
                True,
            )
            else SubscriptionStatus.DISABLED
        )

        subscription.config = await xui.get_wireguard_config(
            inbound,
            subscription.client_email,
        )

        return subscription

    async def delete(
        self,
        xui,
        subscription: Subscription,
    ) -> None:

        await xui.delete_client(
            subscription.client_id
        )

    async def get_file(
        self,
        xui,
        subscription: Subscription,
    ) -> tuple[str, bytes]:

        inbound = await self.get_inbound(
            xui
        )

        if inbound is None:
            raise ValueError(
                "Inbound 'wireguard' не найден"
            )

        config = await xui.get_wireguard_config(
            inbound,
            subscription.client_email,
        )

        return (
            f"{subscription.client_email}.conf",
            config.encode("utf-8"),
        )
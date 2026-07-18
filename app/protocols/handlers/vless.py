import secrets
import string
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import uuid4

from app.config import settings
from app.domain.enums import SubscriptionStatus
from app.domain.inbound import Inbound
from app.domain.subscription import Subscription
from app.protocols.handlers.base import ProtocolHandler
from app.utils.client_email import generate_client_email



def random_string(
    length: int = 16,
) -> str:

    alphabet = (
        string.ascii_lowercase
        + string.digits
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )




class VLESSHandler(
    ProtocolHandler
):

    protocol = "vless"



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
            "password": random_string(16),
            "auth": random_string(16),
            "flow": "xtls-rprx-vision",
            "security": "auto",
            "limitIp": 0,
            "totalGB": 0,
            "expiryTime": int(
                subscription.expires_at.timestamp() * 1000
            ),
            "tgId": 0,
            "reset": 0,
            "group": "",
            "comment": "",
            "enable": True,
        }





    def build_config(
        self,
        subscription: Subscription,
        inbound: Inbound,
    ) -> str:


        reality = (
            inbound.raw["streamSettings"]
            ["realitySettings"]
        )


        params = urlencode(
            {
                "type": "tcp",

                "security": "reality",

                "pbk": reality["settings"]["publicKey"],

                "fp": "chrome",

                "sni": reality["target"].split(":")[0],

                "sid": reality["shortIds"][0],

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




    async def create_subscription(
        self,
        xui,
        user_id: int,
        days: int,
    ) -> Subscription:


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


        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )

        updated = await xui.refresh_inbound(inbound)

        if updated is None:
            raise RuntimeError(
                "Не удалось обновить inbound."
            )

        client = await xui.get_client(
            updated,
            subscription.client_id,
        )

        if client is None:
            raise RuntimeError(
                "Клиент после создания не найден."
            )

        subscription.sub_id = client["subId"]

        links = await xui.get_subscription_links(
            subscription.sub_id,
        )

        if not links:
            raise RuntimeError(
                "3x-ui не вернул ссылку подписки"
            )

        subscription.config = links[0]

        return subscription
    
    async def renew(
        self,
        xui,
        subscription: Subscription,
        days: int,
    ) -> Subscription:


        now = datetime.now()


        expires = max(
            now,
            subscription.expires_at,
        ) + timedelta(
            days=days
        )


        inbound = await self.get_inbound(
            xui
        )


        if inbound is None:
            raise ValueError(
                "Inbound 'vless' не найден"
            )


        updated = await xui.update_client(
            inbound=inbound,
            client_uuid=subscription.client_id,
            expiry_time=int(
                expires.timestamp()
                * 1000
            ),
            enable=True,
        )


        if not updated:

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )


        subscription.expires_at = expires

        subscription.status = (
            SubscriptionStatus.ACTIVE
        )

        if subscription.sub_id:

            links = await xui.get_subscription_links(
                subscription.sub_id,
            )

            if links:
                subscription.config = links[0]

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
                "Inbound 'vless' не найден"
            )


        await xui.set_client_enabled(
            inbound=inbound,
            client_uuid=subscription.client_id,
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


        inbound = await self.get_inbound(
            xui
        )


        if inbound is None:
            raise ValueError(
                "Inbound 'vless' не найден"
            )


        await xui.add_client(
            inbound.id,
            self.build_payload(
                subscription,
                inbound,
            ),
        )


        links = await xui.get_subscription_links(
            subscription.sub_id,
        )

        if not links:
            raise RuntimeError(
                "3x-ui не вернул ссылку подписки"
            )

        subscription.config = links[0]


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
                "Inbound 'vless' не найден"
            )

        # получаем актуальный inbound
        inbound = await xui.refresh_inbound(
            inbound
        )

        if inbound is None:
            raise RuntimeError(
                "Не удалось обновить inbound."
            )

        client = await xui.get_client(
            inbound,
            subscription.client_id,
        )

        if client is None:

            return await self.restore_client(
                xui=xui,
                subscription=subscription,
            )

        subscription.sub_id = client.get(
            "subId",
            subscription.sub_id,
        )

        if subscription.sub_id:

            links = await xui.get_subscription_links(
                subscription.sub_id,
            )

            if links:
                subscription.config = links[0]

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

        return subscription

    async def delete(
        self,
        xui,
        subscription: Subscription,
    ) -> None:

        await xui.delete_client(
            subscription.client_id
        )
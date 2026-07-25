from app.bot.clients.base_api import BaseAPI


class SubscriptionAPI(BaseAPI):

    async def get_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}",
        )

        return response.json()

    async def get_subscription_config(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/config",
        )

        return response.json()

    async def download_file(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/file",
        )

        return response.content

    async def renew_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
        days: int,
    ):

        response = await self._post(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/renew",
            params={
                "days": days,
            },
        )

        return response.json()

    async def get_qr(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/qr",
        )

        return response.content
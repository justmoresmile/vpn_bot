from app.bot.clients.base_api import BaseAPI


class PurchaseAPI(BaseAPI):

    async def create_purchase(
        self,
        telegram_id: int,
        protocol: str,
        days: int,
        subscription_id: int | None = None,
    ):

        response = await self._post(
            telegram_id,
            "/api/v1/purchase/",
            json={
                "protocol": protocol,
                "days": days,
                "subscription_id": subscription_id,
            },
        )

        return response.json()
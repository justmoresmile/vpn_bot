from app.bot.clients.user_api import UserAPI
from app.bot.clients.subscription_api import SubscriptionAPI
from app.bot.clients.purchase_api import PurchaseAPI
from app.bot.clients.admin_api import AdminAPI


class BackendAPIClient(
    UserAPI,
    SubscriptionAPI,
    PurchaseAPI,
    AdminAPI,
):
    """
    Единая точка доступа для Telegram Bot.

    Реальная логика находится в отдельных API-модулях.
    """

    pass


    async def get_admin_user_card(
        self,
        telegram_id: int,
        user_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/users/{user_id}/card",
        )

        return response.json()

api_client = BackendAPIClient()
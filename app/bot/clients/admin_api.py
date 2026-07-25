from app.bot.clients.base_api import BaseAPI


class AdminAPI(BaseAPI):

    async def get_admin_statistics(
        self,
        telegram_id: int,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/statistics",
        )

        return response.json()

    async def get_admin_users(
        self,
        telegram_id: int,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/users",
        )

        return response.json()

    async def get_admin_users_page(
        self,
        telegram_id: int,
        page: int = 1,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/users/page",
            params={
                "page": page,
            },
        )

        return response.json()

    async def get_admin_user(
        self,
        telegram_id: int,
        user_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/users/{user_id}",
        )

        return response.json()

    async def get_admin_user_subscriptions(
        self,
        telegram_id: int,
        user_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/users/{user_id}/subscriptions",
        )

        return response.json()


    async def renew_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
        days: int = 30,
    ):

        response = await self._post(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}/renew",
            params={
                "days": days,
            },
        )

        return response.json()



    async def disable_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._post(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}/disable",
        )

        return response.json()



    async def restore_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._post(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}/restore",
        )

        return response.json()



    async def delete_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._delete(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}",
        )

        return response.json()



    async def get_subscription_config(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}/config",
        )

        return response.json()



    async def get_subscription_file(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/subscriptions/{subscription_id}/file",
        )

        return response

    async def get_admin_subscriptions(
        self,
        telegram_id: int,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/subscriptions",
        )

        return response.json()


    async def get_admin_user_payments(
        self,
        telegram_id: int,
        user_id: int,
    ):

        response = await self._get(
            telegram_id,
            f"/api/v1/admin/users/{user_id}/payments",
        )

        return response.json()

    async def get_admin_payments(
        self,
        telegram_id: int,
        page: int = 1,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/payments",
            params={
                "page": page,
            },
        )

        return response.json()


    async def get_admin_subscriptions(
        self,
        telegram_id: int,
        page: int = 1,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/admin/subscriptions",
            params={
                "page": page,
            },
        )

        return response.json()
from httpx import AsyncClient

from app.bot.clients.base_api import BaseAPI


class UserAPI(BaseAPI):

    async def health(self):

        async with AsyncClient(timeout=10) as client:

            response = await client.get(
                f"{self.base_url}/api/v1/health"
            )

            response.raise_for_status()

            return response.json()

    async def sync_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ):

        async with AsyncClient(timeout=10) as client:

            response = await client.post(
                f"{self.base_url}/api/v1/user/sync",
                json={
                    "telegram_id": telegram_id,
                    "username": username,
                    "first_name": first_name,
                },
            )

            response.raise_for_status()

            return response.json()

    async def get_me(
        self,
        telegram_id: int,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/user/me",
        )

        return response.json()

    async def get_subscriptions(
        self,
        telegram_id: int,
    ):

        response = await self._get(
            telegram_id,
            "/api/v1/user/me/subscriptions",
        )

        return response.json()
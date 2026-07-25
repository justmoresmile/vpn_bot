import httpx

from app.config import settings


class BackendClient:

    def __init__(self):

        self.base_url = (
            settings.backend_api_url.rstrip("/")
        )

        self.api_key = (
            settings.backend_api_key
        )

        self._tokens: dict[int, str] = {}


    async def _authenticate(
        self,
        telegram_id: int,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.base_url}/api/v1/auth/token",
                json={
                    "telegram_id": telegram_id,
                    "api_key": self.api_key,
                },
            )

            response.raise_for_status()

            token = response.json()["access_token"]

            self._tokens[telegram_id] = token

            return token



    async def _request(
        self,
        telegram_id: int,
        method: str,
        endpoint: str,
        **kwargs,
    ):

        token = self._tokens.get(
            telegram_id
        )

        if token is None:

            token = await self._authenticate(
                telegram_id
            )


        headers = kwargs.pop(
            "headers",
            {}
        )


        headers["Authorization"] = (
            f"Bearer {token}"
        )


        async with httpx.AsyncClient() as client:

            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=headers,
                **kwargs,
            )


        if response.status_code == 401:

            token = await self._authenticate(
                telegram_id
            )

            headers["Authorization"] = (
                f"Bearer {token}"
            )


            async with httpx.AsyncClient() as client:

                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{endpoint}",
                    headers=headers,
                    **kwargs,
                )


        response.raise_for_status()

        return response.json()



    async def get(
        self,
        telegram_id: int,
        endpoint: str,
        **kwargs,
    ):

        return await self._request(
            telegram_id,
            "GET",
            endpoint,
            **kwargs,
        )



    async def post(
        self,
        telegram_id: int,
        endpoint: str,
        **kwargs,
    ):

        return await self._request(
            telegram_id,
            "POST",
            endpoint,
            **kwargs,
        )



    async def get_me(
        self,
        telegram_id: int,
    ):

        return await self.get(
            telegram_id,
            "/api/v1/user/me",
        )



    async def get_subscriptions(
        self,
        telegram_id: int,
    ):

        return await self.get(
            telegram_id,
            "/api/v1/user/me/subscriptions",
        )



    async def get_subscription(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        return await self.get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}",
        )



    async def get_config(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        return await self.get(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/config",
        )



    async def renew(
        self,
        telegram_id: int,
        subscription_id: int,
        days: int,
    ):

        return await self.post(
            telegram_id,
            f"/api/v1/subscription/{subscription_id}/renew",
            params={
                "days": days,
            },
        )


backend_client = BackendClient()
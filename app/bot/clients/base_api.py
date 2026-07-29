from datetime import datetime, timedelta

import httpx

from app.config import settings


class BaseAPI:

    def __init__(self):

        self.base_url = settings.backend_api_url.rstrip("/")
        self.api_key = settings.backend_api_key
        

        self._access_token: str | None = None
        self._token_expire: datetime | None = None

    async def login(
        self,
        telegram_id: int,
    ):

        return await self._token(
            telegram_id
        )

    async def _token(
        self,
        telegram_id: int,
    ) -> str:

        if (
            self._access_token
            and self._token_expire
            and datetime.utcnow() < self._token_expire
        ):
            return self._access_token

        async with httpx.AsyncClient(
            timeout=10,
        ) as client:
            print("DEBUG TELEGRAM ID:", telegram_id)
            print("DEBUG SEND KEY:", self.api_key)
            response = await client.post(
                f"{self.base_url}/api/v1/auth/token",
                json={
                    "telegram_id": telegram_id,
                    "api_key": self.api_key,
                },
            )

            response.raise_for_status()

            data = response.json()

            self._access_token = data["access_token"]

            self._token_expire = (
                datetime.utcnow()
                + timedelta(minutes=30)
            )

            return self._access_token

    async def _headers(
        self,
        telegram_id: int,
    ) -> dict:

        token = await self._token(
            telegram_id
        )

        return {
            "Authorization": f"Bearer {token}",
        }

    async def _get(
        self,
        telegram_id: int,
        url: str,
        params: dict | None = None,
    ):

        async with httpx.AsyncClient(
            timeout=10,
        ) as client:

            response = await client.get(
                f"{self.base_url}{url}",
                params=params,
                headers=await self._headers(
                    telegram_id
                ),
            )

            response.raise_for_status()

            return response

    async def _post(
        self,
        telegram_id: int,
        url: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ):

        async with httpx.AsyncClient(
            timeout=10,
        ) as client:

            response = await client.post(
                f"{self.base_url}{url}",
                json=json,
                params=params,
                headers=await self._headers(
                    telegram_id
                ),
            )

            response.raise_for_status()

            return response


    async def _delete(
        self,
        telegram_id: int,
        url: str,
        *,
        params: dict | None = None,
    ):

        async with httpx.AsyncClient(
            timeout=10,
        ) as client:

            response = await client.delete(
                f"{self.base_url}{url}",
                params=params,
                headers=await self._headers(
                    telegram_id
                ),
            )

            response.raise_for_status()

            return response
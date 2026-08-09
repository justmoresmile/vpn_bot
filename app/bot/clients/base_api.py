from datetime import datetime, timedelta

import httpx

from app.config import settings


class BaseAPI:

    def __init__(self):

        self.base_url = settings.backend_api_url.rstrip("/")
        self.api_key = settings.backend_api_key

        self._tokens: dict[
            int,
            tuple[str, datetime],
        ] = {}

    async def login(
        self,
        telegram_id: int,
    ) -> str:

        return await self._token(
            telegram_id,
        )

    async def _token(
        self,
        telegram_id: int,
    ) -> str:

        cached = self._tokens.get(
            telegram_id,
        )

        if cached:

            token, token_expire = cached

            if datetime.utcnow() < token_expire:
                return token

            self._tokens.pop(
                telegram_id,
                None,
            )

        async with httpx.AsyncClient(
            timeout=10,
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/v1/auth/internal/token",
                json={
                    "telegram_id": telegram_id,
                },
                headers={
                    "X-API-Key": self.api_key,
                },
            )

            response.raise_for_status()

            data = response.json()

            token = data["access_token"]

            token_expire = (
                datetime.utcnow()
                + timedelta(minutes=30)
            )

            self._tokens[telegram_id] = (
                token,
                token_expire,
            )

            return token

    async def _headers(
        self,
        telegram_id: int,
    ) -> dict:

        token = await self._token(
            telegram_id,
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
                    telegram_id,
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
                    telegram_id,
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
                    telegram_id,
                ),
            )

            response.raise_for_status()

            return response
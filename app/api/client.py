import httpx

from app.config import settings


class APIClient:

    def __init__(self):
        self.base_url = settings.BACKEND_URL


    async def get_api_key(
        self,
        token: str,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/user/me/api-key",
                headers={
                    "Authorization": f"Bearer {token}"
                },
            )

            if response.status_code != 200:
                return None


            data = response.json()

            return data["api_key"]


api_client = APIClient()
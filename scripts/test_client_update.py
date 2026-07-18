import asyncio
import httpx

from app.repositories.server_repository import server_repo


UUID = "27202b728a6e4bdf"


async def main():
    server = server_repo.get_by_id(1)

    client = httpx.AsyncClient(
        base_url=server.api_url,
        headers={
            "Authorization": f"Bearer {server.api_token}",
            "Content-Type": "application/json",
        },
        verify=False,
    )

    payload = {
        "expiryTime": 1787000000000
    }

    r = await client.post(
        f"/panel/api/clients/update/{UUID}",
        json=payload,
    )

    print(r.status_code)
    print(r.text)

    await client.aclose()


asyncio.run(main())
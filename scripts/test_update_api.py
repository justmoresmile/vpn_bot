import asyncio

import httpx

from app.repositories.server_repository import server_repo


async def main():
    server = server_repo.get_by_id(1)

    client = httpx.AsyncClient(
        base_url=server.api_url,
        headers={
            "Authorization": f"Bearer {server.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        verify=False,
    )

    tests = [
        ("POST", "/panel/api/inbounds/update/1"),
        ("POST", "/panel/api/inbounds/update"),
        ("POST", "/panel/api/inbounds/updateClient"),
        ("POST", "/panel/api/inbounds/updateClient/test"),
        ("POST", "/panel/api/clients/update"),
        ("POST", "/panel/api/clients/update/test"),
        ("POST", "/panel/api/client/update"),
        ("POST", "/panel/api/client/update/test"),
    ]

    for method, url in tests:

        print("=" * 80)
        print(url)

        try:
            r = await client.request(
                method,
                url,
                json={},
            )

            print("STATUS:", r.status_code)

            try:
                print(r.json())
            except Exception:
                print(r.text)

        except Exception as e:
            print(type(e).__name__, e)

    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
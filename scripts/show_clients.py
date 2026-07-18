import asyncio

from app.services.xui_client import XUIClient


async def main():

    client = XUIClient()

    try:

        inbound = await client.get_inbound(
            "vless"
        )

        if inbound is None:
            print("Inbound не найден")
            return


        print(
            "Inbound:",
            inbound.id,
            inbound.remark
        )


        clients = (
            inbound.raw
            .get("settings", {})
            .get("clients", [])
        )


        print("\nКлиенты:")

        for c in clients:

            print(
                "UUID:",
                c.get("id")
            )

            print(
                "Email:",
                c.get("email")
            )

            print(
                "Expiry:",
                c.get("expiryTime")
            )

            print("-" * 40)


    finally:

        await client.close()



if __name__ == "__main__":
    asyncio.run(main())
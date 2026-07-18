import asyncio
from datetime import datetime, timedelta

from app.services.xui_client import XUIClient


CLIENT_UUID = "d3b2b3d3-9245-4589-bc6d-352b848dbe2e"


async def main():

    client = XUIClient()

    try:

        inbound = await client.get_inbound(
            "vless"
        )

        if inbound is None:
            print("Inbound не найден")
            return


        new_expiry = int(
            (
                datetime.now()
                + timedelta(days=60)
            ).timestamp()
            * 1000
        )


        print(
            "Новый expiry:",
            new_expiry
        )


        result = await client.update_client(
            inbound=inbound,
            client_uuid=CLIENT_UUID,
            expiry_time=new_expiry,
        )


        if not result:
            print(
                "Клиент не найден в 3x-ui"
            )
            return


        print(
            "Обновление отправлено."
        )


        # повторная загрузка для проверки

        inbound = await client.get_inbound(
            "vless"
        )


        for client_data in (
            inbound.raw
            .get("settings", {})
            .get("clients", [])
        ):

            if client_data.get("id") == CLIENT_UUID:

                print(
                    "\nКлиент после обновления:"
                )

                print(
                    client_data
                )

                break


    finally:

        await client.close()



if __name__ == "__main__":
    asyncio.run(main())
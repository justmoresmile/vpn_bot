import asyncio

from app.services.xui_client import XUIClient


async def main():

    xui = XUIClient()

    try:

        inbounds = await xui.get_inbounds()

        for inbound in inbounds:

            print("=" * 50)
            print("ID:", inbound.id)
            print("NAME:", inbound.remark)
            print("PROTOCOL:", inbound.protocol)
            print("PORT:", inbound.port)


    finally:

        await xui.close()


if __name__ == "__main__":
    asyncio.run(main())
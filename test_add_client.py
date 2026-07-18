import asyncio
from uuid import uuid4

from app.services.xui_client import XUIClient


async def main():
    xui = XUIClient()

    await xui.add_client(
        1,
        {
            "id": str(uuid4()),
            "email": "test123",
            "password": "123456",
            "auth": "123456",
            "flow": "xtls-rprx-vision",
            "security": "auto",
            "limitIp": 0,
            "totalGB": 0,
            "expiryTime": 0,
            "tgId": 0,
            "subId": "1234567890123456",
            "reset": 0,
            "group": "",
            "comment": "",
            "enable": True,
        },
    )

    await xui.close()


asyncio.run(main())
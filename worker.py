import asyncio

import app.bootstrap

from app.logger import logger
from app.tasks.subscription_task import subscription_task
from app.services.vpn_service import vpn_service


async def main():
    logger.info("JustVPN worker started")

    try:
        await subscription_task()

    finally:
        await vpn_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

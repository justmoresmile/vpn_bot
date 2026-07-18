import asyncio

from loguru import logger

from app.services.subscription_checker import subscription_checker
from app.services.sync_service import sync_service


async def subscription_task():

    logger.info(
        "Subscription task started."
    )

    while True:

        try:

            await sync_service.sync()

            await subscription_checker.run()

        except Exception:

            logger.exception(
                "Subscription task failed."
            )

        await asyncio.sleep(60)
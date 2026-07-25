import asyncio

from loguru import logger

from app.services.subscription_checker import (
    subscription_checker,
)
from app.services.sync_service import (
    sync_service,
)
from app.services.payment_service import (
    payment_service,
)


async def subscription_task():

    logger.info(
        "Background tasks started."
    )

    payment_counter = 0

    while True:

        try:

            await sync_service.sync()

        except Exception:

            logger.exception(
                "Subscription sync failed."
            )

        try:

            await subscription_checker.run()

        except Exception:

            logger.exception(
                "Subscription checker failed."
            )

        try:

            payment_counter += 1

            if payment_counter >= 10:

                payment_service.expire_pending_payments()

                payment_counter = 0

        except Exception:

            logger.exception(
                "Payment checker failed."
            )

        await asyncio.sleep(60)
import asyncio

from loguru import logger

from app.services.billing_service import (
    billing_service,
)
from app.services.subscription_checker import (
    subscription_checker,
)
from app.services.sync_service import (
    sync_service,
)
from app.services.payment_service import (
    payment_service,
)
from app.services.subscription_reminder_service import (
    subscription_reminder_service,
)


async def subscription_task():

    logger.info(
        "Background tasks started."
    )

    payment_counter = 0

    while True:

        # ==============================================
        # BALANCE BILLING
        # ==============================================

        try:

            result = await billing_service.process_due()

            if result["processed"] > 0:

                logger.info(
                    "Balance billing cycle: {}",
                    result,
                )

        except Exception:

            logger.exception(
                "Balance billing failed."
            )

        # ==============================================
        # VPN / PROVIDER SYNC
        # ==============================================

        try:

            await sync_service.sync()

        except Exception:

            logger.exception(
                "Subscription sync failed."
            )

        # ==============================================
        # SUBSCRIPTION REMINDERS
        # ==============================================

        try:

            await subscription_reminder_service.run()

        except Exception:

            logger.exception(
                "Subscription reminder failed."
            )

        # ==============================================
        # SUBSCRIPTION CHECKER
        # ==============================================

        try:

            await subscription_checker.run()

        except Exception:

            logger.exception(
                "Subscription checker failed."
            )

        # ==============================================
        # PENDING PAYMENTS
        # Every 10 cycles = approximately 10 minutes
        # ==============================================

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

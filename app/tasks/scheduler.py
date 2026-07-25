import asyncio

from loguru import logger

from app.services.sync_service import sync_service
from app.services.subscription_checker import subscription_checker
from app.services.payment_service import payment_service


class Scheduler:

    async def run(self):

        logger.info("Scheduler started")

        payment_counter = 0

        while True:

            try:

                await sync_service.sync()

                await subscription_checker.run()

                payment_counter += 1

                if payment_counter >= 10:

                    payment_service.expire_pending_payments()

                    payment_counter = 0

            except Exception:

                logger.exception("Scheduler error")

            await asyncio.sleep(60)


scheduler = Scheduler()
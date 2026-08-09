from loguru import logger


class Scheduler:

    async def run(self):

        logger.info(
            "Scheduler disabled. Use subscription_task."
        )


scheduler = Scheduler()
import asyncio

import uvicorn

from app.api.server import app
from app.bot.app import bot, dp
from app.database.schema import create_tables
from app.logger import logger
from app.services.sync_service import sync_service
from app.tasks.subscription_task import subscription_task


async def run_bot():
    await dp.start_polling(bot)


async def run_api():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

    server = uvicorn.Server(config)

    await server.serve()


async def startup():
    logger.info("Создание базы данных...")

    create_tables()

    logger.success("База данных успешно создана")

    logger.info("Синхронизация подписок...")

    await sync_service.sync()

    logger.success("Синхронизация завершена")

    asyncio.create_task(subscription_task())

    logger.success("SubscriptionChecker запущен")


async def main():
    await startup()

    await asyncio.gather(
        run_bot(),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
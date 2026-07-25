import app.bootstrap
import asyncio
import uvicorn
from app.api.server import app
from app.bot.app import bot, dp
from app.database.schema import create_tables
from app.logger import logger
from app.services.sync_service import sync_service
from app.tasks.scheduler import scheduler
from app.database.seed import seed_database


async def run_bot():
    import os

    print("=" * 50)
    print("BOT STARTED")
    print(os.getpid())
    print("=" * 50)
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
    seed_database()
    logger.success("База данных успешно создана")

    logger.info("Синхронизация подписок...")

    await sync_service.sync()

    logger.success("Синхронизация завершена")

    asyncio.create_task(
    scheduler.run()
    )

    logger.success("SubscriptionChecker запущен")


async def main():
    await startup()

    await asyncio.gather(
        run_bot(),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())


   
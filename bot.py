import asyncio

from aiogram import Bot, Dispatcher

from app.bot.routers import router
from app.config import settings
from app.database.schema import create_tables
from app.logger import logger

from app.services.sync_service import sync_service
from app.tasks.subscription_task import subscription_task


bot = Bot(token=settings.bot_token)

dp = Dispatcher()
dp.include_router(router)


async def main():
    logger.info("Создание базы данных...")

    create_tables()

    logger.success(
        "База данных успешно создана"
    )

    logger.info(
        "Синхронизация подписок с панелью..."
    )

    await sync_service.sync()

    logger.success(
        "Синхронизация завершена"
    )

    asyncio.create_task(
        subscription_task()
    )

    logger.success(
        "SubscriptionChecker запущен"
    )

    logger.success(
        "Бот успешно запущен"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
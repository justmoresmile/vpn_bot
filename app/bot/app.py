import asyncio

from aiogram import Dispatcher

from app.bot.bot_instance import bot
from app.bot.routers import router

from app.logger import logger


dp = Dispatcher()

dp.include_router(router)


async def main():

    logger.success(
        "Бот успешно запущен"
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
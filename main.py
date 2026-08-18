import asyncio
import os

import uvicorn

import app.bootstrap

from app.api.server import app
from app.bot.app import bot, dp
from app.database.schema import create_tables
from app.database.seed import seed_database
from app.logger import logger


async def run_bot():
    print("=" * 50)
    print("BOT STARTED")
    print(os.getpid())
    print("=" * 50)

    await dp.start_polling(bot)


async def run_api():
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
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

async def main():
    await startup()

    await asyncio.gather(
        run_bot(),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())

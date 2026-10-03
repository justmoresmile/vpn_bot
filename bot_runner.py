import asyncio

import app.bootstrap

from app.bot.app import bot, dp
from app.logger import logger


async def main():
    logger.info("JustVPN Telegram bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

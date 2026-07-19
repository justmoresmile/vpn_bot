from aiogram import Bot, Dispatcher

from app.bot.routers import router
from app.config import settings

bot = Bot(token=settings.bot_token)

dp = Dispatcher()
dp.include_router(router)
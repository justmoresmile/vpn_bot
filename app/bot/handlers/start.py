from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.miniapp import (
    miniapp_keyboard,
)


router = Router()


WELCOME_TEXT = """
👋 <b>Добро пожаловать в JustVPN</b>

Быстрый и удобный VPN без сложных настроек.

🔐 Безопасное подключение
📱 Управление устройствами
🌍 Выбор VPN-сервера
💳 Баланс и тариф в одном месте
💬 Поддержка прямо в приложении

Всё управление JustVPN доступно
в нашем приложении.

Нажмите кнопку ниже 👇
"""


@router.message(CommandStart())
async def start(
    message: Message,
):

    await message.answer(
        WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=miniapp_keyboard,
    )

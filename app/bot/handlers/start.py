from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.clients.api_client import api_client
from app.bot.keyboards.main_menu import main_menu


router = Router()


WELCOME_TEXT = """
🚀 <b>Добро пожаловать!</b>

Ваш быстрый и безопасный VPN уже готов к подключению.

🔐 Защищённое соединение WireGuard
⚡ Мгновенная активация после оплаты
📱 Поддержка всех популярных устройств
🌍 Стабильный доступ без ограничений

Чтобы начать, выберите в меню:
🚀 Получить VPN
"""


RETURN_TEXT = """
👋 <b>С возвращением!</b>

Ваш VPN всегда под рукой.

🔐 Проверить активную подписку:
👤 Мой VPN

Выберите действие ниже 👇
"""


@router.message(CommandStart())
async def start(
    message: Message,
):

    try:

        result = await api_client.sync_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

        text = (
            WELCOME_TEXT
            if result["created"]
            else RETURN_TEXT
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=main_menu,
        )

    except Exception:

        await message.answer(
            "❌ Не удалось подключиться к серверу."
        )
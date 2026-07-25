from aiogram import Router
from aiogram.types import Message

from app.bot.clients.api_client import api_client
from app.logger import logger


router = Router()


@router.message(lambda message: message.text == "👤 Профиль")
async def profile(message: Message):

    try:

        user = await api_client.get_me(
            telegram_id=message.from_user.id,
        )

        subscriptions = await api_client.get_subscriptions(
            telegram_id=message.from_user.id,
        )

        active_count = sum(
            1
            for sub in subscriptions
            if sub["status"] == "active"
        )

        username = (
            f"@{user['username']}"
            if user["username"]
            else "не указан"
        )

        text = (
            "👤 <b>Ваш профиль</b>\n\n"
            f"🆔 ID: <code>{user['telegram_id']}</code>\n"
            f"👤 Имя: {user['first_name'] or 'не указано'}\n"
            f"📛 Username: {username}\n\n"
            f"📊 Всего подписок: {len(subscriptions)}\n"
            f"✅ Активных: {active_count}"
        )

        await message.answer(
            text,
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Profile loading failed")

        await message.answer(
            "❌ Не удалось загрузить профиль."
        )
from aiogram import Router
from aiogram.types import Message

from app.repositories.user_repository import users_repo
from app.services.vpn_service import vpn_service


router = Router()


@router.message(lambda message: message.text == "👤 Профиль")
async def profile(message: Message):

    user = users_repo.get_by_telegram(
        message.from_user.id
    )

    if user is None:
        await message.answer(
            "Пользователь не найден."
        )
        return


    # Синхронизация данных Telegram -> SQLite
    users_repo.update_profile(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )


    # Получаем свежие данные после обновления
    user = users_repo.get_by_telegram(
        message.from_user.id
    )


    subscriptions = vpn_service.get_by_user(
        user.id
    )


    active_count = sum(
        1
        for sub in subscriptions
        if sub.status == "active"
    )


    username = (
        f"@{user.username}"
        if user.username
        else "не указан"
    )


    text = (
        "👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{user.telegram_id}</code>\n"
        f"👤 Имя: {user.first_name or 'не указано'}\n"
        f"📛 Username: {username}\n\n"
        f"📊 Всего подписок: {len(subscriptions)}\n"
        f"✅ Активных: {active_count}"
    )


    await message.answer(
        text,
        parse_mode="HTML",
    )

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards.main_menu import main_menu
from app.domain.user import User
from app.repositories.user_repository import users_repo

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    user = users_repo.get_by_telegram(message.from_user.id)

    if user is None:

        user = User(
            id=None,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            is_admin=False,
        )

        users_repo.create(user)

        text = (
            f"👋 Добро пожаловать, {message.from_user.first_name}!\n\n"
            "Вы успешно зарегистрированы."
        )

    else:

        users_repo.update_profile(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )

        text = (
            f"👋 С возвращением, {message.from_user.first_name}!"
        )

    await message.answer(
        text,
        reply_markup=main_menu,
    )


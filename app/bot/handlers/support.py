from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)

from app.ui.screens.support import support_screen
from app.bot.keyboards.support_menu import support_menu

router = Router()


@router.message(F.text == "💬 Поддержка")
async def support(message: Message):

    await message.answer(
        support_screen(),
        parse_mode="HTML",
        reply_markup=support_menu(),
    )


@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery):

    await callback.message.answer(
        support_screen(),
        parse_mode="HTML",
        reply_markup=support_menu(),
    )

    await callback.answer()
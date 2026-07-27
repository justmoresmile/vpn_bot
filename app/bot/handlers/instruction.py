from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
)

from app.bot.keyboards.main_menu import main_menu
from app.ui.screens.instruction import vpn_instruction_screen
from app.ui.screens.common import support_screen

router = Router()


@router.callback_query(
    F.data == "vpn_instruction"
)
async def vpn_instruction(
    callback: CallbackQuery,
):

    await callback.message.answer(
        vpn_instruction_screen(),
        parse_mode="HTML",
        reply_markup=main_menu,
    )

    await callback.answer()


@router.message(
    F.text == "📖 Инструкция"
)
async def instruction_menu_handler(
    message: Message,
):

    await message.answer(
        vpn_instruction_screen(),
        parse_mode="HTML",
        reply_markup=main_menu,
    )
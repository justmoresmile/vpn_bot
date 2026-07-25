from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def support_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Открыть поддержку",
                    url="https://t.me/suppport_vpn_bot",
                )
            ],
        ]
    )
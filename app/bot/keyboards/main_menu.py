from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🚀 Получить VPN"
            ),
        ],
        [
            KeyboardButton(
                text="👤 Мой VPN"
            ),
            KeyboardButton(
                text="📖 Инструкция"
            ),
        ],
        [
            KeyboardButton(
                text="💬 Поддержка"
            ),
        ],
    ],
    resize_keyboard=True,
)
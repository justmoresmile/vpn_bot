from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


protocol_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="VLESS"),
            KeyboardButton(text="WireGuard"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ],
    resize_keyboard=True,
)
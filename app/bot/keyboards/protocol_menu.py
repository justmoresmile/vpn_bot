from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.config import settings


keyboard = []

row = []

if settings.enable_vless:
    row.append(
        KeyboardButton(text="VLESS")
    )

row.append(
    KeyboardButton(text="WireGuard")
)

keyboard.append(row)

keyboard.append(
    [
        KeyboardButton(text="⬅️ Назад"),
    ]
)

protocol_menu = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True,
)
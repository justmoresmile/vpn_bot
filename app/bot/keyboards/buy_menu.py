from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

buy_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 30 дней"),
            KeyboardButton(text="📅 90 дней"),
        ],
        [
            KeyboardButton(text="📅 180 дней"),
            KeyboardButton(text="📅 365 дней"),
        ],
        [
            KeyboardButton(text="⬅️ Назад"),
        ],
    ],
    resize_keyboard=True,
)
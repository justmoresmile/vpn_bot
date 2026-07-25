from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


buy_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="⭐ 1 месяц — 150 ₽"
            ),
        ],
        [
            KeyboardButton(
                text="🔥 3 месяца — 420 ₽ (-7%)"
            ),
        ],
        [
            KeyboardButton(
                text="💎 6 месяцев — 800 ₽ (-11%)"
            ),
        ],
        [
            KeyboardButton(
                text="🏆 1 год — 1500 ₽ (-17%)"
            ),
        ],
        [
            KeyboardButton(
                text="🏠 Главное меню"
            ),
        ],
    ],
    resize_keyboard=True,
)
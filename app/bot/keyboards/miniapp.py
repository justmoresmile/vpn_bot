from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)

from app.config import settings


miniapp_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Открыть JustFastVPN",
                web_app=WebAppInfo(
                    url=settings.miniapp_url,
                ),
            ),
        ],
    ],
)
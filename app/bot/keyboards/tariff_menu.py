from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def tariff_menu(
    renew: bool = False,
    subscription_id: int | None = None,
) -> InlineKeyboardMarkup:

    if renew:

        if subscription_id is None:
            raise ValueError(
                "subscription_id required"
            )

        def callback(days: int):
            return (
                f"renew_buy:{subscription_id}:{days}"
            )

    else:

        def callback(days: int):
            return f"buy:{days}"

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="⭐ 1 месяц • 150 ₽",
                    callback_data=callback(30),
                ),
            ],

            [
                InlineKeyboardButton(
                    text="🔥 3 месяца • 420 ₽ (-7%)",
                    callback_data=callback(90),
                ),
            ],

            [
                InlineKeyboardButton(
                    text="💎 6 месяцев • 800 ₽ (-11%)",
                    callback_data=callback(180),
                ),
            ],

            [
                InlineKeyboardButton(
                    text="🏆 1 год • 1500 ₽ (-17%)",
                    callback_data=callback(365),
                ),
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="main_menu",
                ),
            ],

        ]
    )
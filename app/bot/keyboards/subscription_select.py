from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def subscription_select_menu(subscriptions):

    buttons = []


    for sub in subscriptions:

        buttons.append(
            [
                InlineKeyboardButton(
                    text="👤 Мой VPN",
                    callback_data=f"select_subscription:{sub.id}",
                )
            ]
        )


    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
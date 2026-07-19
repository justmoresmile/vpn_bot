from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def subscriptions_list_menu(subscriptions):

    keyboard = []

    for sub in subscriptions:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="👤 Мой VPN",
                    callback_data=f"select_subscription:{sub.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )



def subscription_actions_menu(
    subscription,
):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📥 Скачать конфиг",
                    callback_data=(
                        f"subscription_config:{subscription.id}"
                    ),
                )
            ],

            [
                InlineKeyboardButton(
                    text="📷 QR-код",
                    callback_data=(
                        f"subscription_qr:{subscription.id}"
                    ),
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔄 Продлить",
                    callback_data=(
                        f"subscription_renew:{subscription.id}"
                    ),
                )
            ],

        ]
    )



def renew_menu(
    subscription_id: int,
):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="30 дней",
                    callback_data=(
                        f"renew_30:{subscription_id}"
                    ),
                ),

                InlineKeyboardButton(
                    text="90 дней",
                    callback_data=(
                        f"renew_90:{subscription_id}"
                    ),
                ),
            ],

            [
                InlineKeyboardButton(
                    text="180 дней",
                    callback_data=(
                        f"renew_180:{subscription_id}"
                    ),
                ),

                InlineKeyboardButton(
                    text="365 дней",
                    callback_data=(
                        f"renew_365:{subscription_id}"
                    ),
                ),
            ],

        ]
    )
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def _subscription_id(subscription):

    if isinstance(subscription, dict):
        return subscription["id"]

    return subscription.id


def subscriptions_list_menu(subscriptions):

    keyboard = []

    for subscription in subscriptions:

        subscription_id = _subscription_id(
            subscription
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="👤 Мой VPN",
                    callback_data=f"select_subscription:{subscription_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )


def subscription_actions_menu(subscription):

    subscription_id = _subscription_id(
        subscription
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📥 Скачать конфиг",
                    callback_data=f"subscription_config:{subscription_id}",
                )
            ],

            [
                InlineKeyboardButton(
                    text="📷 QR-код",
                    callback_data=f"subscription_qr:{subscription_id}",
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔄 Продлить",
                    callback_data=f"subscription_renew:{subscription_id}",
                )
            ],

        ]
    )
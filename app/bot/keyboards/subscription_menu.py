from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def subscriptions_list_menu(subscriptions):

    keyboard = []

    for index, sub in enumerate(
        subscriptions,
        start=1,
    ):

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📦 Подписка #{index} ({sub.protocol.upper()})",
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

    keyboard = []

    if subscription.protocol == "wireguard":

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="📁 Скачать конфиг",
                    callback_data=f"subscription_config:{subscription.id}",
                )
            ]
        )

    else:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="📷 QR Code",
                    callback_data=f"subscription_qr:{subscription.id}",
                )
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="📋 Конфигурация",
                    callback_data=f"subscription_config:{subscription.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔄 Продлить",
                callback_data=f"subscription_renew:{subscription.id}",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard,
    )


def renew_menu(
    subscription_id: int,
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="30 дней",
                    callback_data=f"renew_30:{subscription_id}",
                ),
                InlineKeyboardButton(
                    text="90 дней",
                    callback_data=f"renew_90:{subscription_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="180 дней",
                    callback_data=f"renew_180:{subscription_id}",
                ),
                InlineKeyboardButton(
                    text="365 дней",
                    callback_data=f"renew_365:{subscription_id}",
                ),
            ],
        ]
    )
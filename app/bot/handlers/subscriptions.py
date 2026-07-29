from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

from app.bot.clients.api_client import api_client

from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
)

from app.ui.screens.subscription import (
    my_vpn_screen,
    no_subscription_screen,
)


router = Router()


@router.message(F.text == "👤 Мой VPN")
async def my_vpn(
    message: Message,
):

    try:

        subscriptions = await api_client.get_subscriptions(
            message.from_user.id
        )

    except Exception as e:

        await message.answer(
            f"❌ Ошибка: {e}"
        )

        return


    if not subscriptions:

        await message.answer(
            no_subscription_screen(),
            parse_mode="HTML",
        )

        return


    subscription = subscriptions[0]


    expires = datetime.fromisoformat(
        subscription["expires_at"]
    )


    days_left = max(
        0,
        (
            expires - datetime.now()
        ).days,
    )


    await message.answer(

        my_vpn_screen(
            subscription=subscription,
            days_left=days_left,
        ),

        parse_mode="HTML",

        reply_markup=subscription_actions_menu(
            subscription
        ),
    )
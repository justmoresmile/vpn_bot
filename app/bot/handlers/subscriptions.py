from datetime import datetime
import traceback

from aiogram import F, Router
from aiogram.types import Message


from app.bot.clients.api_client import api_client

from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
)

from app.ui.screens.subscription import (
    subscription_screen,
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


        if (
            subscription["status"] == "active"
            and days_left > 0
        ):

            status = "🟢 <b>Подписка активна</b>"


        elif subscription["status"] == "active":

            status = "🟠 <b>Подписка истекла</b>"


        else:

            status = "🔴 <b>Подписка неактивна</b>"



        await message.answer(

            subscription_screen(

                status=status,

                expires=expires.strftime(
                    "%d.%m.%Y %H:%M"
                ),

                days_left=days_left,

                protocol=subscription["protocol"].title(),

            ),

            parse_mode="HTML",

            reply_markup=subscription_actions_menu(
                subscription
            ),

        )


    except Exception:

        traceback.print_exc()


        await message.answer(
            "❌ Внутренняя ошибка."
        )
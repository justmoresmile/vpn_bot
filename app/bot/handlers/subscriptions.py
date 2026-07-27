from aiogram import F, Router
from aiogram.types import Message

from app.bot.clients.api_client import api_client

from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
)

from app.ui.screens.subscription import (
    subscription_screen,
    no_subscription_screen,
)


router = Router()


@router.message(F.text == "👤 Мой VPN")
async def my_vpn(
    message: Message,
):

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


    await message.answer(

        subscription_screen(
            subscription
        ),

        parse_mode="HTML",

        reply_markup=subscription_actions_menu(
            subscription
        ),
    )
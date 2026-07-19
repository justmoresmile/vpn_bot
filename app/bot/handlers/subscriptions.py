from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

from app.bot.keyboards.subscription_select import subscription_select_menu
from app.repositories.user_repository import users_repo
from app.services.vpn_service import vpn_service
from app.domain.legacy_enums import SubscriptionStatus


router = Router()


@router.message(F.text == "📊 Мои подписки")
async def subscriptions(message: Message):

    user = users_repo.get_by_telegram(
        message.from_user.id
    )

    if user is None:

        await message.answer(
            "❌ Пользователь не найден."
        )

        return


    subscriptions = vpn_service.get_by_user(
        user.id
    )


    if not subscriptions:

        await message.answer(
            "📭 У вас пока нет VPN подписки."
        )

        return



    text = (
        "👤 <b>Мой VPN</b>\n\n"
    )


    for index, sub in enumerate(
        subscriptions,
        start=1,
    ):


        try:

            sub = await vpn_service.sync_subscription(
                sub
            )


        except Exception as e:

            print(
                f"[VPN] Failed to sync subscription {sub.id}: {e}"
            )



        days_left = max(
            0,
            (
                sub.expires_at
                -
                datetime.now()
            ).days,
        )



        if sub.status == SubscriptionStatus.ACTIVE:

            if days_left > 0:
                status = "✅ Активен"

            else:
                status = "❌ Истёк"

        else:

            status = "❌ Неактивен"



        text += (

            f"🔐 <b>Статус:</b>\n"
            f"{status}\n\n"

            f"📦 <b>Подписка:</b>\n"
            f"{(sub.expires_at - sub.created_at).days} дней\n\n"

            f"⏳ <b>Действует до:</b>\n"
            f"{sub.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"

            f"⌛ <b>Осталось:</b>\n"
            f"{days_left} дней\n\n"

        )



    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=subscription_select_menu(
            subscriptions
        ),
    )
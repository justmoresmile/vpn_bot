from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

from app.repositories.user_repository import users_repo
from app.services.vpn_service import vpn_service
from app.domain.legacy_enums import SubscriptionStatus
from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
)


router = Router()


@router.message(F.text == "👤 Мой VPN")
async def my_vpn(message: Message):

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


    # Берём один активный VPN
    subscription = subscriptions[0]


    try:

        subscription = await vpn_service.sync_subscription(
            subscription
        )

    except Exception as e:

        print(
            f"[VPN] Sync failed: {e}"
        )



    days_left = max(
        0,
        (
            subscription.expires_at
            -
            datetime.now()
        ).days,
    )


    if subscription.status == SubscriptionStatus.ACTIVE:

        if days_left > 0:
            status = "✅ Активен"

        else:
            status = "❌ Истёк"

    else:

        status = "❌ Неактивен"



    subscription_days = (
        subscription.expires_at
        -
        subscription.created_at
    ).days



    text = (

        "👤 <b>Мой VPN</b>\n\n"

        "🔐 <b>Статус:</b>\n"
        f"{status}\n\n"

        "📦 <b>Подписка:</b>\n"
        f"{subscription_days} дней\n\n"

        "⏳ <b>Действует до:</b>\n"
        f"{subscription.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"

        "⌛ <b>Осталось:</b>\n"
        f"{days_left} дней"

    )


    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=subscription_actions_menu(
            subscription
        ),
    )
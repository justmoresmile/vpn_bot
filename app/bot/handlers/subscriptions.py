from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

from app.bot.keyboards.subscription_select import subscription_select_menu
from app.config import settings
from app.repositories.user_repository import users_repo
from app.services.vpn_service import vpn_service
from app.domain.enums import SubscriptionStatus
from app.bot.keyboards.subscription_menu import subscriptions_list_menu


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
            "📭 У вас пока нет подписок."
        )
        return


    text = "📦 <b>Мои подписки</b>\n\n"


    for index, sub in enumerate(
        subscriptions,
        start=1
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

            if days_left > 7:
                status = "🟢 Активна"

            elif days_left > 3:
                status = "🟡 Скоро закончится"

            elif days_left > 0:
                status = "🟠 Заканчивается"

            else:
                status = "🔴 Истекла"

        else:
            status = "🔴 Неактивна"



        text += (
            "━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>Подписка #{index}</b>\n\n"
            f"{status}\n\n"
            f"🔒 <b>Протокол:</b> "
            f"{sub.protocol.upper()}\n"
            f"📅 <b>Осталось:</b> "
            f"{days_left} дней\n"
            f"📆 <b>До:</b> "
            f"{sub.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )


    text += (
        f"🌍 <b>Сервер:</b> {settings.vpn_name}\n"
        f"🌐 <b>Хост:</b> {settings.vpn_host}\n\n"
        "💡 После окончания подписки VPN перестанет работать."
    )


    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=subscription_select_menu(
            subscriptions
        ),
)
  
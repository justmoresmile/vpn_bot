from datetime import datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile

from app.repositories.subscription_repository import subscription_repo
from app.services.vpn_service import vpn_service
from app.services.qr_service import qr_service
from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
    renew_menu,
)


router = Router()



def get_subscription(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    return subscription_repo.get_by_id(
        subscription_id
    )



@router.callback_query(
    F.data.startswith("select_subscription:")
)
async def select_subscription(
    callback: CallbackQuery,
):

    subscription = get_subscription(
        callback
    )


    if subscription is None:

        await callback.answer(
            "VPN не найден",
            show_alert=True,
        )

        return



    days_left = max(
        0,
        (
            subscription.expires_at
            -
            datetime.now()
        ).days,
    )



    total_days = (
        subscription.expires_at
        -
        subscription.created_at
    ).days



    await callback.message.answer(
        (
            "👤 <b>Мой VPN</b>\n\n"

            "🔐 <b>Статус:</b>\n"
            "✅ Активен\n\n"

            "📦 <b>Подписка:</b>\n"
            f"{total_days} дней\n\n"

            "⏳ <b>Действует до:</b>\n"
            f"{subscription.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"

            "⌛ <b>Осталось:</b>\n"
            f"{days_left} дней"
        ),
        parse_mode="HTML",
        reply_markup=subscription_actions_menu(
            subscription,
        ),
    )


    await callback.answer()




@router.callback_query(
    F.data.startswith("subscription_qr:")
)
async def qr(
    callback: CallbackQuery,
):

    subscription = get_subscription(
        callback
    )


    if subscription is None:
        return



    config = await vpn_service.get_wireguard_config(
        subscription
    )


    photo = qr_service.generate(
        config
    )


    await callback.message.answer_photo(
        photo,
        caption="📷 WireGuard QR-код",
    )


    await callback.answer()




@router.callback_query(
    F.data.startswith("subscription_config:")
)
async def config(
    callback: CallbackQuery,
):

    subscription = get_subscription(
        callback
    )


    if subscription is None:
        return



    config = await vpn_service.get_wireguard_config(
        subscription
    )


    file = BufferedInputFile(
        config.encode("utf-8"),
        filename=f"{subscription.client_email}.conf",
    )


    await callback.message.answer_document(
        document=file,
        caption="📥 WireGuard конфигурация",
    )


    await callback.answer()




@router.callback_query(
    F.data.startswith("subscription_renew:")
)
async def renew(
    callback: CallbackQuery,
):

    subscription = get_subscription(
        callback
    )


    if subscription is None:
        return



    await callback.message.answer(
        "📅 Выберите срок продления",
        reply_markup=renew_menu(
            subscription.id,
        ),
    )


    await callback.answer()




async def do_renew(
    callback: CallbackQuery,
    days: int,
):

    subscription = get_subscription(
        callback
    )


    if subscription is None:
        return



    subscription = await vpn_service.renew(
        subscription.id,
        days,
    )



    await callback.message.answer(
        "✅ VPN продлён\n\n"
        "⏳ Действует до:\n"
        f"<b>{subscription.expires_at.strftime('%d.%m.%Y %H:%M')}</b>",
        parse_mode="HTML",
    )


    await callback.answer()




@router.callback_query(
    F.data.startswith("renew_30:")
)
async def renew30(
    callback: CallbackQuery,
):

    await do_renew(
        callback,
        30,
    )




@router.callback_query(
    F.data.startswith("renew_90:")
)
async def renew90(
    callback: CallbackQuery,
):

    await do_renew(
        callback,
        90,
    )




@router.callback_query(
    F.data.startswith("renew_180:")
)
async def renew180(
    callback: CallbackQuery,
):

    await do_renew(
        callback,
        180,
    )




@router.callback_query(
    F.data.startswith("renew_365:")
)
async def renew365(
    callback: CallbackQuery,
):

    await do_renew(
        callback,
        365,
    )
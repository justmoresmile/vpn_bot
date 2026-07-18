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


def get_subscription(callback: CallbackQuery):

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
            "Подписка не найдена",
            show_alert=True,
        )

        return

    await callback.message.answer(
        (
            "📦 <b>Подписка</b>\n\n"
            f"🔒 <b>Протокол:</b> {subscription.protocol.upper()}\n"
            f"📅 <b>До:</b> "
            f"{subscription.expires_at.strftime('%d.%m.%Y %H:%M')}"
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

    photo = qr_service.generate(
        subscription.config
    )

    await callback.message.answer_photo(
        photo,
        caption="📷 QR Code",
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

    if subscription.protocol == "wireguard":
        config = await vpn_service.get_wireguard_config(
            subscription
        )


        await callback.message.answer_document(
            BufferedInputFile(
                config.encode("utf-8"),
                filename=f"{subscription.client_email}.conf",
            ),
            caption="📁 WireGuard конфигурация",
        )

    else:

        await callback.message.answer(
            "📋 <b>Конфигурация</b>\n\n"
            f"<code>{subscription.config}</code>",
            parse_mode="HTML",
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
        "✅ Подписка продлена\n\n"
        f"До <b>{subscription.expires_at.strftime('%d.%m.%Y %H:%M')}</b>",
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
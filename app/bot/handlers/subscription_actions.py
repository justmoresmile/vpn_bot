from datetime import datetime

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    BufferedInputFile,
)

from app.bot.clients.api_client import api_client
from app.bot.keyboards.subscription_menu import (
    subscription_actions_menu,
)
from app.bot.keyboards.tariff_menu import tariff_menu

from app.ui.screens_old import my_vpn_screen


router = Router()


def get_subscription_id(
    callback: CallbackQuery,
) -> int:

    return int(
        callback.data.split(":")[1]
    )


@router.callback_query(
    F.data.startswith("select_subscription:")
)
async def select_subscription(
    callback: CallbackQuery,
):

    subscription_id = get_subscription_id(
        callback
    )

    subscription = await api_client.get_subscription(
        telegram_id=callback.from_user.id,
        subscription_id=subscription_id,
    )

    expires = datetime.fromisoformat(
        subscription["expires_at"]
    )

    created = datetime.fromisoformat(
        subscription["created_at"]
    )

    days_left = max(
        0,
        (
            expires - datetime.now()
        ).days,
    )

    total_days = (
        expires - created
    ).days

    status = (
        "🟢 Активен"
        if days_left > 0
        else "🔴 Истёк"
    )

    await callback.message.answer(
        my_vpn_screen(
            status=status,
            days=total_days,
            expires=expires.strftime(
                "%d.%m.%Y %H:%M"
            ),
            left=days_left,
            protocol=subscription["protocol"].title(),
            server="Россия",
        ),
        parse_mode="HTML",
        reply_markup=subscription_actions_menu(
            subscription
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("subscription_qr:")
)
async def qr(
    callback: CallbackQuery,
):

    try:

        subscription_id = get_subscription_id(
            callback
        )

        image = await api_client.get_qr(
            telegram_id=callback.from_user.id,
            subscription_id=subscription_id,
        )

        await callback.message.answer_photo(
            BufferedInputFile(
                image,
                filename="vpn_qr.png",
            ),
            caption="📷 QR-код WireGuard",
        )

    except Exception:

        from app.logger import logger

        logger.exception(
            "QR download failed"
        )

        await callback.answer(
            "Не удалось получить QR",
            show_alert=True,
        )

    else:

        await callback.answer()


    
@router.callback_query(
    F.data.startswith("subscription_config:")
)
async def config(
    callback: CallbackQuery,
):

    subscription_id = get_subscription_id(
        callback
    )


    subscription = await api_client.get_subscription(
        telegram_id=callback.from_user.id,
        subscription_id=subscription_id,
    )


    content = await api_client.download_file(
        telegram_id=callback.from_user.id,
        subscription_id=subscription_id,
    )


    client_email = subscription.get(
        "client_email",
        str(callback.from_user.id),
    )


    await callback.message.answer_document(
        BufferedInputFile(
            content,
            filename=f"{client_email}.conf",
        ),
        caption="📥 Конфигурационный файл",
    )


    await callback.answer()





@router.callback_query(
    F.data.startswith("subscription_renew:")
)
async def renew(
    callback: CallbackQuery,
):

    subscription_id = get_subscription_id(
        callback
    )

    await callback.message.answer(
        "Выберите срок продления:",
        reply_markup=tariff_menu(
            renew=True,
            subscription_id=subscription_id,
        ),
    )

    async def get_qr(
        self,
        telegram_id: int,
        subscription_id: int,
    ):

        async with httpx.AsyncClient(
            timeout=10
        ) as client:

            response = await client.get(
                f"{self.base_url}/api/v1/subscription/{subscription_id}/qr",
                headers=await self._headers(
                    telegram_id
                ),
            )

            response.raise_for_status()

            return response.content



    await callback.answer()
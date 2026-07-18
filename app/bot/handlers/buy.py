import traceback

from aiogram import F, Router
from aiogram.types import (
    Message,
    BufferedInputFile,
)

from app.bot.keyboards.buy_menu import buy_menu
from app.bot.keyboards.main_menu import main_menu
from app.bot.keyboards.protocol_menu import protocol_menu

from app.repositories.user_repository import users_repo

from app.services.qr_service import qr_service
from app.services.vpn_service import vpn_service


router = Router()


BUY_DAYS = {
    "📅 30 дней": 30,
    "📅 90 дней": 90,
    "📅 180 дней": 180,
    "📅 365 дней": 365,
}


selected_protocol: dict[int, str] = {}


@router.message(F.text == "🛒 Купить/продлить VPN")
async def buy(message: Message):

    await message.answer(
        "🔌 Выберите протокол:",
        reply_markup=protocol_menu,
    )


@router.message(F.text.in_(["VLESS", "WireGuard"]))
async def choose_protocol(message: Message):

    selected_protocol[
        message.from_user.id
    ] = (
        "vless"
        if message.text == "VLESS"
        else "wireguard"
    )

    await message.answer(
        "📦 Выберите срок:",
        reply_markup=buy_menu,
    )


@router.message(F.text.in_(BUY_DAYS))
async def buy_subscription(message: Message):

    protocol = selected_protocol.get(
        message.from_user.id,
        "vless",
    )

    await create_subscription(
        message=message,
        protocol=protocol,
        days=BUY_DAYS[message.text],
    )


@router.message(F.text == "⬅️ Назад")
async def back(message: Message):

    await message.answer(
        "Главное меню",
        reply_markup=main_menu,
    )


async def create_subscription(
    message: Message,
    protocol: str,
    days: int,
):

    try:

        user = users_repo.get_by_telegram(
            message.from_user.id,
        )

        if user is None:

            await message.answer(
                "❌ Пользователь не найден.",
                reply_markup=main_menu,
            )

            return

        subscription = await vpn_service.purchase(
            user_id=user.id,
            protocol=protocol,
            days=days,
        )

        caption = (
            "✅ <b>VPN готов!</b>\n\n"
            f"🔌 Протокол: <b>{subscription.protocol.upper()}</b>\n"
            f"📅 Срок: <b>{days} дней</b>"
        )

        if subscription.protocol == "wireguard":

            config = await vpn_service.get_wireguard_config(
                subscription
            )
            await message.answer_document(
                BufferedInputFile(
                    config.encode("utf-8"),
                    filename=f"{subscription.client_email}.conf",
                ),
                caption=caption,
                parse_mode="HTML",
                reply_markup=main_menu,
            )
            return

        photo = qr_service.generate(
            subscription.config,
        )

        await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="HTML",
        )

        await message.answer(
            "📋 <b>Конфигурация:</b>\n\n"
            f"<code>{subscription.config}</code>",
            parse_mode="HTML",
            reply_markup=main_menu,
        )

    except Exception:

        traceback.print_exc()

        await message.answer(
            "❌ Ошибка при создании VPN.",
            reply_markup=main_menu,
        )
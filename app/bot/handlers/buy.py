import traceback

from aiogram import F, Router
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.bot.keyboards.buy_menu import buy_menu
from app.bot.keyboards.main_menu import main_menu
from app.bot.keyboards.protocol_menu import protocol_menu

from app.repositories.user_repository import users_repo

from app.services.qr_service import qr_service
from app.services.vpn_service import vpn_service
from app.services.payment_service import payment_service




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



        payment = payment_service.create_payment(
            user_id=user.id,
            protocol=protocol,
            days=days,
        )


        if payment.confirmation_url is None:

            await message.answer(
                "❌ Не удалось создать ссылку оплаты.",
                reply_markup=main_menu,
            )

            return


        keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 Оплатить",
                            url=payment.confirmation_url,
                        )
                    ],
                ]
            )
        await message.answer(
            (
                "💳 <b>Оплата VPN</b>\n\n"
                f"🔌 Протокол: <b>{protocol.upper()}</b>\n"
                f"📅 Срок: <b>{days} дней</b>\n"
                f"💰 Сумма: <b>{payment.amount} ₽</b>\n\n"
            "После успешной оплаты VPN будет создан автоматически.\n"
            "Конфиг придёт в этот чат."
            ),
            parse_mode="HTML",
            reply_markup=keyboard,
        )


    except Exception:

        from app.logger import logger

        logger.exception(
            "Payment creation failed"
        )


        await message.answer(
            "❌ Ошибка при создании платежа.",
            reply_markup=main_menu,
        )

from aiogram import F, Router
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.bot.clients.api_client import api_client

from app.bot.keyboards.tariff_menu import tariff_menu
from app.bot.keyboards.main_menu import main_menu

from app.ui.screens_old import (
    buy_screen,
    payment_screen,
)


router = Router()


TARIFF_NAMES = {
    30: "⭐ 1 месяц",
    90: "🔥 3 месяца",
    180: "💎 6 месяцев",
    365: "🏆 1 год",
}


@router.message(F.text == "🚀 Получить VPN")
async def buy(message: Message):

    await message.answer(
        buy_screen(),
        parse_mode="HTML",
        reply_markup=tariff_menu(),
    )


@router.callback_query(F.data.startswith("buy:"))
async def buy_subscription(
    callback: CallbackQuery,
):

    days = int(
        callback.data.split(":")[1]
    )

    await create_subscription(
        message=callback.message,
        days=days,
    )

    await callback.answer()


@router.callback_query(F.data.startswith("renew_buy:"))
async def renew_subscription(
    callback: CallbackQuery,
):

    _, subscription_id, days = callback.data.split(":")

    await create_subscription(
        message=callback.message,
        days=int(days),
        subscription_id=int(subscription_id),
    )

    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main_callback(
    callback: CallbackQuery,
):

    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu,
    )

    await callback.answer()


@router.message(F.text == "🏠 Главное меню")
async def back_to_main(
    message: Message,
):

    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu,
    )


async def create_subscription(
    message: Message,
    days: int,
    subscription_id: int | None = None,
):

    try:

        payment = await api_client.create_purchase(
            telegram_id=message.chat.id,
            protocol="wireguard",
            days=days,
            subscription_id=subscription_id,
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💳 Оплатить",
                        url=payment["confirmation_url"],
                    )
                ]
            ]
        )

        await message.answer(
            payment_screen(
                tariff=TARIFF_NAMES[days],
                price=payment["amount"],
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
            "❌ Ошибка создания платежа.",
            reply_markup=main_menu,
        )
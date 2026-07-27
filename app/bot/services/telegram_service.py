from aiogram.enums import ParseMode

from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.bot.bot_instance import bot

from app.bot.clients.api_client import api_client

from app.logger import logger

from app.ui.screens.payment import (
    payment_success_screen,
    payment_renew_success_screen,
)

from app.bot.keyboards.subscription_menu import (
    subscription_expire_menu,
)
from app.ui.screens.subscription import (
    subscription_renew_success_screen,
)

import re



def safe_filename(value: str) -> str:

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        value,
    )



class TelegramService:



    async def send_subscription(
        self,
        user_id: int,
        subscription,
    ) -> None:


        logger.info(
            f"send_subscription() called for user {user_id}"
        )


        try:


            subscription_id = (
                subscription["id"]
                if isinstance(subscription, dict)
                else subscription.id
            )


            data = await api_client.download_file(
                telegram_id=user_id,
                subscription_id=subscription_id,
            )



            client_email = (
                subscription["client_email"]
                if isinstance(subscription, dict)
                else subscription.client_email
            )



            filename = (
                f"{safe_filename(client_email)}.conf"
            )



            file = BufferedInputFile(
                data,
                filename=filename,
            )



            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📖 Инструкция по подключению",
                            callback_data="vpn_instruction",
                        )
                    ]
                ]
            )



            await bot.send_message(
                chat_id=user_id,
                text=payment_success_screen(),
                parse_mode=ParseMode.HTML,
            )


            await bot.send_document(
                chat_id=user_id,
                document=file,
                reply_markup=keyboard,
            )



        except Exception:


            logger.exception(
                "Не удалось отправить VPN пользователю %s",
                user_id,
            )

            raise




    async def send_renew_notification(
        self,
        user_id: int,
        old_date: str,
        new_date: str,
    ) -> None:



        await bot.send_message(
            chat_id=user_id,
            text=payment_renew_success_screen(
                old_date=old_date,
                new_date=new_date,
            ),
            parse_mode=ParseMode.HTML,
        )



    async def send_admin_renew_notification(
        self,
        user_id: int,
        old_date: str,
        new_date: str,
    ):

        await bot.send_message(
            chat_id=user_id,
            text=subscription_renew_success_screen(
                old_date=old_date,
                new_date=new_date,
            ),
            parse_mode=ParseMode.HTML,
        )

    async def send_expire_warning(
        self,
        user_id: int,
        days: int,
        expires_at,
        subscription,
    ) -> None:



        keyboard = subscription_expire_menu(
            subscription
        )



        if days == 7:


            text = (
                "⚠️ <b>Напоминание JustVPN</b>\n\n"
                "Ваша подписка заканчивается через "
                "<b>7 дней</b>.\n\n"
                f"📅 <b>Дата окончания:</b>\n"
                f"<b>{expires_at:%d.%m.%Y}</b>\n\n"
                "❤️ Продлите подписку заранее,\n"
                "чтобы VPN работал без перерывов."
            )



        elif days == 3:


            text = (
                "⚠️ <b>Напоминание JustVPN</b>\n\n"
                "До окончания вашей подписки осталось "
                "<b>3 дня</b>.\n\n"
                f"📅 <b>Дата окончания:</b>\n"
                f"<b>{expires_at:%d.%m.%Y}</b>\n\n"
                "❤️ Не забудьте продлить подписку."
            )



        else:


            text = (
                "🚨 <b>Последний день JustVPN</b>\n\n"
                "Сегодня заканчивается ваша подписка.\n\n"
                f"📅 <b>Дата окончания:</b>\n"
                f"<b>{expires_at:%d.%m.%Y}</b>\n\n"
                "Завтра VPN будет отключен.\n\n"
                "❤️ Продлите подписку сейчас."
            )



        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )





    async def send_message(
        self,
        user_id: int,
        text: str,
    ):



        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )





telegram_service = TelegramService()
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

            filename = f"{safe_filename(client_email)}.conf"


            file = BufferedInputFile(
                data,
                filename=filename,
            )


            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📖 Как подключить VPN",
                            callback_data="vpn_instruction",
                        )
                    ]
                ]
            )


            await bot.send_document(
                chat_id=user_id,
                document=file,
                caption=payment_success_screen(),
                parse_mode=ParseMode.HTML,
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
import os
import re

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


# ============================================================
# PUBLIC SUBSCRIPTION URL
# ============================================================

# Для теста можно указать IP сервера:
#
# PUBLIC_SUBSCRIPTION_BASE_URL=http://195.82.146.104:8000
#
# В будущем:
#
# PUBLIC_SUBSCRIPTION_BASE_URL=https://s.justvpn.com
#
PUBLIC_SUBSCRIPTION_BASE_URL = os.getenv(
    "PUBLIC_SUBSCRIPTION_BASE_URL",
    "http://195.82.146.104:8000",
).rstrip("/")


# ============================================================
# HELPERS
# ============================================================


def safe_filename(value: str) -> str:

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        value,
    )


def build_subscription_url(
    subscription_token: str,
) -> str:

    return (
        f"{PUBLIC_SUBSCRIPTION_BASE_URL}"
        f"/{subscription_token}"
    )


# ============================================================
# TELEGRAM SERVICE
# ============================================================


class TelegramService:

    # ========================================================
    # SEND SUBSCRIPTION
    # ========================================================

    async def send_subscription(
        self,
        user_id: int,
        subscription,
    ) -> None:

        logger.info(
            "send_subscription() called for user %s",
            user_id,
        )

        try:

            # ------------------------------------------------
            # SUBSCRIPTION ID
            # ------------------------------------------------

            subscription_id = (
                subscription["id"]
                if isinstance(subscription, dict)
                else subscription.id
            )

            # ------------------------------------------------
            # PROTOCOL
            # ------------------------------------------------

            protocol = (
                subscription["protocol"]
                if isinstance(subscription, dict)
                else subscription.protocol
            )

            protocol = protocol.lower().strip()

            # ------------------------------------------------
            # CLIENT EMAIL
            # ------------------------------------------------

            client_email = (
                subscription["client_email"]
                if isinstance(subscription, dict)
                else subscription.client_email
            )

            # ------------------------------------------------
            # KEYBOARD
            # ------------------------------------------------

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

            # =================================================
            # VLESS
            # =================================================

            if protocol == "vless":

                logger.info(
                    "Preparing VLESS subscription link: "
                    "user=%s subscription=%s",
                    user_id,
                    subscription_id,
                )

                # ---------------------------------------------
                # GET TOKEN
                # ---------------------------------------------

                subscription_token = (
                    subscription["subscription_token"]
                    if isinstance(subscription, dict)
                    else subscription.subscription_token
                )

                if not subscription_token:

                    raise RuntimeError(
                        "VLESS subscription token not found"
                    )

                # ---------------------------------------------
                # BUILD SHORT URL
                # ---------------------------------------------

                subscription_url = build_subscription_url(
                    subscription_token
                )

                logger.info(
                    "Generated public subscription URL: "
                    "user=%s subscription=%s url=%s",
                    user_id,
                    subscription_id,
                    subscription_url,
                )

                # ---------------------------------------------
                # SEND MESSAGE
                # ---------------------------------------------

                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        "✅ <b>Оплата успешно прошла!</b>\n\n"
                        "Ваш VPN создан.\n\n"
                        "🔗 <b>Ваша подписка:</b>\n\n"
                        f"<code>{subscription_url}</code>\n\n"
                        "👆 Нажмите на ссылку, "
                        "чтобы открыть подписку."
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )

                logger.success(
                    "VLESS subscription URL sent successfully: "
                    "user=%s subscription=%s",
                    user_id,
                    subscription_id,
                )

                return

            # =================================================
            # WIREGUARD
            # =================================================

            if protocol == "wireguard":

                logger.info(
                    "Sending WireGuard configuration: "
                    "user=%s subscription=%s",
                    user_id,
                    subscription_id,
                )

                # ---------------------------------------------
                # DOWNLOAD CONFIG
                # ---------------------------------------------

                data = await api_client.download_file(
                    telegram_id=user_id,
                    subscription_id=subscription_id,
                )

                # ---------------------------------------------
                # FILE NAME
                # ---------------------------------------------

                filename = (
                    f"{safe_filename(client_email)}.conf"
                )

                file = BufferedInputFile(
                    data,
                    filename=filename,
                )

                # ---------------------------------------------
                # SUCCESS MESSAGE
                # ---------------------------------------------

                await bot.send_message(
                    chat_id=user_id,
                    text=payment_success_screen(),
                    parse_mode=ParseMode.HTML,
                )

                # ---------------------------------------------
                # SEND FILE
                # ---------------------------------------------

                await bot.send_document(
                    chat_id=user_id,
                    document=file,
                    reply_markup=keyboard,
                )

                logger.success(
                    "WireGuard configuration sent successfully: "
                    "user=%s subscription=%s",
                    user_id,
                    subscription_id,
                )

                return

            # =================================================
            # UNKNOWN PROTOCOL
            # =================================================

            raise ValueError(
                f"Unsupported subscription protocol: {protocol}"
            )

        except Exception:

            logger.exception(
                "Не удалось отправить VPN пользователю %s",
                user_id,
            )

            raise

    # ========================================================
    # RENEW NOTIFICATION
    # ========================================================

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

    # ========================================================
    # ADMIN RENEW NOTIFICATION
    # ========================================================

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

    # ========================================================
    # EXPIRE WARNING
    # ========================================================

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

    # ========================================================
    # GENERIC MESSAGE
    # ========================================================

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


# ============================================================
# SINGLETON
# ============================================================

telegram_service = TelegramService()
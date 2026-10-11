import html

from aiogram.enums import ParseMode

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from app.bot.bot_instance import bot

from app.config import settings

from app.logger import logger


# ============================================================
# TELEGRAM SERVICE
# ============================================================


class TelegramService:

    # ========================================================
    # SUPPORT TOPIC
    # ========================================================

    async def create_support_topic(
        self,
        *,
        chat_id: int,
        ticket_id: int,
        user_id: int,
        telegram_id: int | None,
        username: str | None,
        subject: str,
        message: str,
    ) -> int:

        safe_subject = html.escape(
            subject
        )

        topic_name = (
            f"#{ticket_id} • {subject}"
        )[:128]

        topic = await bot.create_forum_topic(
            chat_id=chat_id,
            name=topic_name,
        )

        thread_id = (
            topic.message_thread_id
        )

        if username:
            safe_username = html.escape(
                username.lstrip("@")
            )
            user_text = (
                f"@{safe_username}"
            )
        else:
            user_text = "не указан"

        telegram_text = (
            str(telegram_id)
            if telegram_id
            else "не привязан"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Закрыть обращение",
                        callback_data=(
                            f"support_topic_close:{ticket_id}"
                        ),
                    ),
                ]
            ]
        )

        header_message = await bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=(
                f"🆘 <b>Обращение #{ticket_id}</b>\n\n"
                f"👤 <b>Клиент:</b> {user_text}\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
                f"📱 <b>Telegram ID:</b> "
                f"<code>{telegram_text}</code>\n"
                f"📌 <b>Тема:</b> {safe_subject}\n\n"
                f"💬 <b>Первое сообщение:</b>\n"
                f"{html.escape(message)}"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        )

        try:
            await bot.pin_chat_message(
                chat_id=chat_id,
                message_id=header_message.message_id,
                disable_notification=True,
            )
        except Exception:
            logger.exception(
                "Failed to pin support ticket header: "
                "ticket=%s",
                ticket_id,
            )

        logger.info(
            "Support topic created: "
            "ticket=%s thread=%s",
            ticket_id,
            thread_id,
        )

        return thread_id


    async def send_support_topic_message(
        self,
        *,
        chat_id: int,
        thread_id: int,
        sender: str,
        message: str,
        username: str | None = None,
    ) -> None:

        if sender == "user":

            if username:
                safe_username = html.escape(
                    username.lstrip("@")
                )

                title = (
                    f"👤 <b>@{safe_username}</b>"
                )
            else:
                title = "👤 <b>Пользователь</b>"
        elif sender == "admin":
            title = "🛠 <b>Поддержка</b>"
        else:
            title = "ℹ️ <b>Система</b>"

        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=(
                f"{title}\n\n"
                f"{html.escape(message)}"
            ),
            parse_mode=ParseMode.HTML,
        )


    async def close_support_topic(
        self,
        *,
        chat_id: int,
        thread_id: int,
        ticket_id: int,
        subject: str,
    ) -> None:

        topic_name = (
            f"✅ #{ticket_id} • {subject}"
        )[:128]

        try:
            await bot.edit_forum_topic(
                chat_id=chat_id,
                message_thread_id=thread_id,
                name=topic_name,
            )
        except Exception:
            logger.exception(
                "Failed to rename support topic: "
                "ticket=%s thread=%s",
                ticket_id,
                thread_id,
            )

        try:
            await bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="✅ <b>Обращение закрыто</b>",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.exception(
                "Failed to send support close message: "
                "ticket=%s thread=%s",
                ticket_id,
                thread_id,
            )

        await bot.close_forum_topic(
            chat_id=chat_id,
            message_thread_id=thread_id,
        )


    async def delete_support_topic(
        self,
        *,
        chat_id: int,
        thread_id: int,
    ) -> None:

        await bot.delete_forum_topic(
            chat_id=chat_id,
            message_thread_id=thread_id,
        )


    # ========================================================
    # GENERIC MESSAGE
    # ========================================================

    async def send_user_notification(
        self,
        *,
        telegram_id: int,
        title: str,
        message: str,
    ) -> None:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🚀 Открыть JustVPN",
                        web_app=WebAppInfo(
                            url=settings.miniapp_url,
                        ),
                    )
                ]
            ]
        )

        await bot.send_message(
            chat_id=telegram_id,
            text=(
                f"<b>{html.escape(title)}</b>\n\n"
                f"{html.escape(message)}"
            ),
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


# ============================================================
# SINGLETON
# ============================================================

telegram_service = TelegramService()
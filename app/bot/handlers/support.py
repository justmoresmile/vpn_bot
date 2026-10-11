from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)

from app.config import settings

from app.services.support_service import (
    support_service,
)

from app.repositories.support_repository import (
    support_repo,
)

from app.bot.services.telegram_service import (
    telegram_service,
)


router = Router()


SUPPORT_CHAT_ID = -1004442060823


# ============================================================
# TELEGRAM TOPIC -> MINI APP
# ============================================================

@router.message(
    F.chat.id == SUPPORT_CHAT_ID
)
async def support_topic_message_to_ticket(
    message: Message,
):

    if not message.message_thread_id:
        return

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    # В поддержку пишет только администратор.
    if (
        message.from_user.id
        != settings.admin_id
    ):
        return

    if not message.text:
        return

    # Служебные Telegram-команды пользователю
    # как сообщения поддержки не отправляем.
    if message.text.startswith("/"):
        return

    ticket = (
        support_repo.get_by_telegram_thread_id(
            message.message_thread_id
        )
    )

    if ticket is None:
        return

    if ticket.status == "closed":

        await message.reply(
            "⚠️ Это обращение уже закрыто."
        )

        return

    support_service.add_admin_message(
        admin_id=message.from_user.id,
        ticket_id=ticket.id,
        message=message.text,
    )


# ============================================================
# CLOSE TICKET BUTTON
# ============================================================

@router.callback_query(
    F.data.startswith(
        "support_topic_close:"
    )
)
async def support_topic_close_button(
    callback: CallbackQuery,
):

    if (
        not callback.from_user
        or callback.from_user.id
        != settings.admin_id
    ):

        await callback.answer(
            "Нет доступа",
            show_alert=True,
        )

        return

    try:

        ticket_id = int(
            callback.data.split(
                ":",
                1,
            )[1]
        )

        ticket = (
            support_service.get_ticket(
                ticket_id
            )
        )

        if ticket.status == "closed":

            await callback.answer(
                "Обращение уже закрыто",
                show_alert=True,
            )

            return

        if not ticket.telegram_thread_id:

            await callback.answer(
                "У обращения нет Telegram-темы",
                show_alert=True,
            )

            return

        support_service.close_ticket_admin(
            ticket_id=ticket.id
        )

        await callback.answer(
            "Обращение закрыто"
        )

        await telegram_service.close_support_topic(
            chat_id=SUPPORT_CHAT_ID,
            thread_id=ticket.telegram_thread_id,
            ticket_id=ticket.id,
            subject=ticket.subject,
        )

    except Exception as exc:

        await callback.answer(
            str(exc),
            show_alert=True,
        )

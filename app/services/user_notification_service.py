from loguru import logger

from app.repositories.notification_repository import (
    notification_repo,
)
from app.repositories.user_repository import (
    users_repo,
)
from app.bot.services.telegram_service import (
    telegram_service,
)


class UserNotificationService:

    async def send_once(
        self,
        *,
        user_id: int,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ):

        notification = (
            notification_repo.create_event(
                user_id=user_id,
                event_key=event_key,
                notification_type=(
                    notification_type
                ),
                title=title,
                message=message,
                related_type=related_type,
                related_id=related_id,
            )
        )

        if notification is None:
            raise RuntimeError(
                "Failed to create notification"
            )

        if bool(
            notification["telegram_sent"]
        ):
            return notification

        user = users_repo.get_by_id(
            user_id
        )

        if (
            user is None
            or user.telegram_id is None
        ):
            return notification

        try:

            await (
                telegram_service
                .send_user_notification(
                    telegram_id=(
                        user.telegram_id
                    ),
                    title=title,
                    message=message,
                )
            )

        except Exception:

            logger.exception(
                "Telegram notification failed "
                "user={} event={}",
                user_id,
                event_key,
            )

            return notification

        notification_repo.mark_telegram_sent(
            notification["id"]
        )

        return notification


user_notification_service = (
    UserNotificationService()
)

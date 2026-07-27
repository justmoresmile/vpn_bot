from datetime import datetime, timezone

from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.repositories.user_repository import (
    users_repo,
)

from app.bot.services.telegram_service import (
    telegram_service,
)

from app.database.database import db


class SubscriptionReminderService:


    async def run(self):

        subscriptions = (
            subscription_repo.get_active()
        )

        now = datetime.now(
            timezone.utc
        )


        for subscription in subscriptions:

            if not subscription.expires_at:
                continue


            days_left = (
                subscription.expires_at.date()
                -
                now.date()
            ).days


            if days_left not in [7, 3, 1]:
                continue


            notification_type = (
                f"expires_{days_left}_days"
            )


            exists = db.fetchone(
                """
                SELECT id
                FROM subscription_notifications
                WHERE subscription_id = ?
                AND notification_type = ?
                AND expires_at = ?
                """,
                (
                    subscription.id,
                    notification_type,
                    int(
                        subscription.expires_at.timestamp()
                    ),
                ),
            )


            if exists:
                continue


            user = users_repo.get_by_id(
                subscription.user_id
            )


            if user is None:

                logger.warning(
                    "User not found subscription={}",
                    subscription.id,
                )

                continue


            try:

                await telegram_service.send_expire_warning(
                    user_id=user.telegram_id,
                    days=days_left,
                    expires_at=subscription.expires_at,
                    subscription=subscription,
                )


                db.execute(
                """
                INSERT INTO subscription_notifications
                (
                    subscription_id,
                    notification_type,
                    expires_at,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                    (
                        subscription.id,
                        notification_type,
                        int(
                            subscription.expires_at.timestamp()
                        ),
                        int(
                            datetime.now().timestamp()
                        ),
                    ),
                )


                logger.info(
                    "Subscription reminder sent "
                    "subscription={} days={}",
                    subscription.id,
                    days_left,
                )


            except Exception:

                logger.exception(
                    "Reminder failed subscription={}",
                    subscription.id,
                )



subscription_reminder_service = (
    SubscriptionReminderService()
)
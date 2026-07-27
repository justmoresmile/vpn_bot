from datetime import datetime, timezone

from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.repositories.users_repository import (
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
                """,
                (
                    subscription.id,
                    notification_type,
                ),
            )


            if exists:
                continue



            user = users_repo.get_by_id(
                subscription.user_id
            )


            if not user:
                continue



            try:

                if days_left == 7:

                    text = (
                        "⚠️ Напоминание JustVPN\n\n"
                        "Ваша подписка закончится через 7 дней.\n\n"
                        f"📅 Дата окончания: "
                        f"{subscription.expires_at:%d.%m.%Y}\n\n"
                        "Продлите подписку заранее ❤️"
                    )


                elif days_left == 3:

                    text = (
                        "⚠️ Ваша подписка JustVPN\n\n"
                        "Осталось 3 дня до окончания."
                    )


                else:

                    text = (
                        "🚨 Последний день JustVPN\n\n"
                        "Завтра подписка будет отключена."
                    )



                await telegram_service.send_message(
                    user.telegram_id,
                    text,
                )



                db.execute(
                    """
                    INSERT INTO subscription_notifications
                    (
                        subscription_id,
                        notification_type,
                        created_at
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        subscription.id,
                        notification_type,
                        int(
                            datetime.now().timestamp()
                        ),
                    ),
                )


                logger.info(
                    "Reminder sent subscription={} days={}",
                    subscription.id,
                    days_left,
                )



            except Exception:

                logger.exception(
                    "Reminder failed {}",
                    subscription.id,
                )



subscription_reminder_service = (
    SubscriptionReminderService()
)
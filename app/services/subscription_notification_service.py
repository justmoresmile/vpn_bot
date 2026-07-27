from datetime import datetime, timedelta

from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.repositories.users_repository import (
    users_repo,
)

from app.database.database import db

from app.bot.bot_instance import bot


class SubscriptionNotificationService:


    async def check(self):

        subscriptions = (
            subscription_repo.get_active()
        )

        if not subscriptions:
            return


        now = datetime.now()


        for subscription in subscriptions:

            try:

                days_left = (
                    subscription.expires_at - now
                ).days


                if days_left not in [
                    7,
                    3,
                    1,
                ]:
                    continue


                notification_type = (
                    f"expires_{days_left}_days"
                )


                already_sent = db.fetchone(
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


                if already_sent:
                    continue



                user = (
                    users_repo.get_by_id(
                        subscription.user_id
                    )
                )


                if not user:
                    continue



                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=(
                        "🔔 Напоминание о подписке\n\n"
                        f"Ваша подписка закончится "
                        f"через {days_left} дн.\n\n"
                        "Продлите подписку, чтобы "
                        "не потерять доступ к VPN."
                    ),
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
                    "Notification sent: subscription={} days={}",
                    subscription.id,
                    days_left,
                )


            except Exception:

                logger.exception(
                    "Subscription notification failed {}",
                    subscription.id,
                )



subscription_notification_service = (
    SubscriptionNotificationService()
)
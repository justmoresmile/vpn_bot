from datetime import datetime, timezone

from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.bot.services.telegram_service import (
    telegram_service,
)


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


            try:


                if days_left == 7:

                    await telegram_service.send_message(
                        subscription.user_id,
                        (
                            "⚠️ Напоминание JustVPN\n\n"
                            "Ваша подписка закончится через 7 дней.\n\n"
                            f"📅 Дата окончания: "
                            f"{subscription.expires_at:%d.%m.%Y}\n\n"
                            "Продлите подписку заранее ❤️"
                        )
                    )


                elif days_left == 3:

                    await telegram_service.send_message(
                        subscription.user_id,
                        (
                            "⚠️ Ваша подписка JustVPN\n\n"
                            "Осталось 3 дня до окончания."
                        )
                    )


                elif days_left == 1:

                    await telegram_service.send_message(
                        subscription.user_id,
                        (
                            "🚨 Последний день JustVPN\n\n"
                            "Завтра подписка будет отключена."
                        )
                    )


            except Exception:

                logger.exception(
                    "Reminder failed {}",
                    subscription.id,
                )



subscription_reminder_service = (
    SubscriptionReminderService()
)
from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.services.vpn_service import (
    vpn_service,
)
from app.repositories.subscription_notification_repository import (
    subscription_notification_repo,
)

from app.bot.services.telegram_service import (
    telegram_service,
)


class SubscriptionChecker:

    async def run(self):

        await self.check_expiring()


        subscriptions = (
            subscription_repo.get_expired_active()
        )

        if not subscriptions:

            logger.debug(
                "Expired subscriptions not found."
            )

            return

        logger.info(
            "Checking {} expired subscriptions.",
            len(subscriptions),
        )

        for subscription in subscriptions:

            try:

                await vpn_service.disable(
                    subscription
                )

                logger.info(
                    "Subscription {} expired.",
                    subscription.id,
                )

            except Exception:

                logger.exception(
                    "Failed to expire subscription {}",
                    subscription.id,
                )


        async def check_expiring(self):

            periods = [
                7,
                3,
                1,
            ]


            for days in periods:


                subscriptions = (
                    subscription_repo.get_expiring(days)
                )


                for subscription in subscriptions:


                    notification_type = (
                        f"expire_{days}"
                    )


                    if subscription_notification_repo.exists(
                        subscription.id,
                        notification_type,
                    ):
                        continue



                    await telegram_service.send_expire_warning(
                        user_id=subscription.user_id,
                        days=days,
                        expires_at=(
                            subscription.expires_at
                            .strftime(
                                "%d.%m.%Y %H:%M"
                            )
                        ),
                    )


                    subscription_notification_repo.create(
                        subscription.id,
                        notification_type,
                    )


                    logger.info(
                        "Expiration warning sent for subscription {} ({})",
                        subscription.id,
                        days,
                    )


subscription_checker = SubscriptionChecker()
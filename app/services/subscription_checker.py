from loguru import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.services.vpn_service import (
    vpn_service,
)


class SubscriptionChecker:

    async def run(self):

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


subscription_checker = SubscriptionChecker()
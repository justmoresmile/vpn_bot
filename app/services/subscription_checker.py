from loguru import logger

from app.repositories.subscription_repository import subscription_repo
from app.services.xui_client import XUIClient
from app.domain.enums import SubscriptionStatus


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

        xui = XUIClient()

        try:

            for subscription in subscriptions:

                try:

                    inbound = await xui.get_inbound(
                        subscription.protocol
                    )

                    if inbound is None:

                        logger.warning(
                            "Inbound '{}' not found.",
                            subscription.protocol,
                        )

                        continue

                    await xui.set_client_enabled(
                        inbound=inbound,
                        client_uuid=subscription.client_id,
                        enabled=False,
                    )

                    subscription.status = SubscriptionStatus.EXPIRED

                    subscription_repo.update(
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

        finally:

            await xui.close()


subscription_checker = SubscriptionChecker()
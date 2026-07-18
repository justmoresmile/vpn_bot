from loguru import logger

from app.repositories.subscription_repository import subscription_repo
from app.services.vpn_service import vpn_service


class SyncService:

    async def sync(self):

        subscriptions = (
            subscription_repo.get_all()
        )

        total = len(subscriptions)

        if total == 0:

            logger.debug(
                "No subscriptions to synchronize."
            )

            return

        logger.info(
            "Synchronizing {} subscriptions.",
            total,
        )

        success = 0

        for subscription in subscriptions:

            try:

                await vpn_service.sync_subscription(
                    subscription
                )

                success += 1


            except Exception:

                logger.exception(
                    "Failed to synchronize subscription {}",
                    subscription.id,
                )



        logger.info(
            "Synchronization finished ({}/{}).",
            success,
            total,
        )


sync_service = SyncService()
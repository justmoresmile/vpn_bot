from datetime import datetime

from app.domain.subscription import Subscription

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.services.vpn_service import (
    vpn_service,
)

from app.logger import logger


class SubscriptionService:


    def get_by_id(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        return subscription_repo.get_by_id(
            subscription_id
        )


    def get_by_user(
        self,
        user_id: int,
    ) -> list[Subscription]:

        return subscription_repo.get_by_user(
            user_id
        )


    def get_active_by_user(
        self,
        user_id: int,
    ) -> Subscription | None:

        return subscription_repo.get_active_by_user(
            user_id
        )


    def update(
        self,
        subscription: Subscription,
    ):

        subscription_repo.update(
            subscription
        )


    async def get_config(
        self,
        subscription_id: int,
    ):

        return await vpn_service.get_config(
            subscription_id
        )


    async def get_file(
        self,
        subscription: Subscription,
    ):

        return await vpn_service.get_file(
            subscription
        )


    async def renew(
        self,
        subscription_id: int,
        days: int,
    ):

        return await vpn_service.renew(
            subscription_id,
            days,
        )


    async def disable_expired(
        self,
    ):

        subscriptions = (
            subscription_repo.get_expired_active()
        )

        if not subscriptions:

            return

        logger.info(
            "Found {} expired subscriptions",
            len(subscriptions),
        )

        for subscription in subscriptions:

            try:

                await vpn_service.disable(
                    subscription.id
                )

                logger.info(
                    "Subscription {} disabled",
                    subscription.id,
                )

            except Exception:

                logger.exception(
                    "Failed to disable subscription {}",
                    subscription.id,
                )


    async def sync_all(
        self,
    ):

        subscriptions = (
            subscription_repo.get_active()
        )

        logger.info(
            "Sync {} active subscriptions",
            len(subscriptions),
        )

        for subscription in subscriptions:

            try:

                await vpn_service.sync_subscription(
                    subscription
                )

            except Exception:

                logger.exception(
                    "Sync failed for subscription {}",
                    subscription.id,
                )


subscription_service = SubscriptionService()
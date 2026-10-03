from datetime import datetime, timedelta

from loguru import logger

from app.domain.enums.subscription_status import (
    SubscriptionStatus,
)
from app.repositories.user_repository import (
    users_repo,
)
from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.services.vpn_service import (
    vpn_service,
)
from app.services.remnawave_service import (
    remnawave_service,
)


TRIAL_DURATION = timedelta(days=3)


class TrialService:

    async def start(
        self,
        user_id: int,
    ):

        user = users_repo.get_by_id(
            user_id
        )

        if user is None:
            raise ValueError(
                "User not found"
            )

        if user.trial_used:
            raise RuntimeError(
                "Trial already used"
            )

        subscriptions = (
            subscription_repo.get_by_user(
                user_id
            )
        )

        # Trial даём только новому пользователю.
        # Даже удалённая/истёкшая старая подписка означает,
        # что пользователь уже пользовался сервисом.
        if subscriptions:
            raise RuntimeError(
                "Trial is available only for new users"
            )

        started_at = datetime.now()
        ends_at = (
            started_at
            + TRIAL_DURATION
        )

        claimed = users_repo.claim_trial(
            user_id=user_id,
            started_at=started_at,
            ends_at=ends_at,
        )

        if not claimed:
            raise RuntimeError(
                "Trial already used"
            )

        try:

            subscription = (
                await vpn_service
                .create_balance_subscription(
                    user_id=user_id,
                    protocol="vless",
                )
            )

            provider_user = (
                remnawave_service.ensure_user(
                    justvpn_user_id=user_id,
                    expire_at=ends_at,
                    hwid_device_limit=(
                        subscription.device_limit
                    ),
                )
            )

            remote_status = str(
                provider_user.get(
                    "status",
                    "",
                )
            ).upper()

            if remote_status != "ACTIVE":
                remnawave_service.enable_user(
                    user_id
                )

            subscription.status = (
                SubscriptionStatus.ACTIVE
            )

            subscription.billing_mode = (
                "balance"
            )

            subscription.billing_enabled = True

            # В trial деньги ещё не списывались.
            subscription.billing_day_index = 0

            subscription.paid_until = (
                ends_at
            )

            subscription.expires_at = (
                ends_at
            )

            subscription_repo.update(
                subscription
            )

            logger.info(
                "Trial started "
                "user={} subscription={} "
                "started_at={} ends_at={}",
                user_id,
                subscription.id,
                started_at,
                ends_at,
            )

            return {
                "status": "active",
                "subscription_id": (
                    subscription.id
                ),
                "trial_started_at": (
                    started_at.isoformat()
                ),
                "trial_ends_at": (
                    ends_at.isoformat()
                ),
                "billing_mode": (
                    subscription.billing_mode
                ),
                "billing_day_index": (
                    subscription.billing_day_index
                ),
            }

        except Exception:

            users_repo.release_trial(
                user_id=user_id,
                started_at=started_at,
            )

            logger.exception(
                "Trial start failed user={}",
                user_id,
            )

            raise


trial_service = TrialService()

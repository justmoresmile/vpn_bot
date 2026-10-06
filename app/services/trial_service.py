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
from app.repositories.wallet_repository import (
    wallet_repo,
)
from app.services.pricing_service import (
    get_daily_price_kopecks,
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

    async def finish(
        self,
        user_id: int,
        device_limit: int,
    ):

        user = users_repo.get_by_id(
            user_id
        )

        if user is None:
            raise ValueError(
                "User not found"
            )

        if (
            device_limit < 1
            or device_limit > 10
        ):
            raise ValueError(
                "Device limit must be between 1 and 10"
            )

        now = datetime.now()

        if (
            not user.trial_used
            or user.trial_ends_at is None
            or user.trial_ends_at <= now
        ):
            raise RuntimeError(
                "Trial is not active"
            )

        subscriptions = (
            subscription_repo.get_by_user(
                user_id
            )
        )

        subscription = next(
            (
                item
                for item in subscriptions
                if (
                    item.billing_mode == "balance"
                    and item.status
                    != SubscriptionStatus.DELETED
                )
            ),
            None,
        )

        if subscription is None:
            raise RuntimeError(
                "Balance subscription not found"
            )

        original_trial_ends_at = (
            user.trial_ends_at
        )

        original_device_limit = (
            subscription.device_limit
        )

        claimed = (
            users_repo.claim_trial_finish(
                user_id=user_id,
                current_ends_at=(
                    original_trial_ends_at
                ),
                finished_at=now,
            )
        )

        if not claimed:
            raise RuntimeError(
                "Trial finish already in progress"
            )

        daily_price_kopecks = (
            get_daily_price_kopecks(
                device_limit
            )
        )

        new_balance = None
        charged = False

        try:

            new_balance = wallet_repo.debit(
                user_id=user_id,
                amount_kopecks=(
                    daily_price_kopecks
                ),
                transaction_type=(
                    "trial_finish_charge"
                ),
                description=(
                    f"Trial finish charge "
                    f"subscription #{subscription.id} "
                    f"devices={device_limit}"
                ),
            )

            if new_balance is None:

                users_repo.restore_trial_finish(
                    user_id=user_id,
                    finished_at=now,
                    original_ends_at=(
                        original_trial_ends_at
                    ),
                )

                return {
                    "status": (
                        "insufficient_balance"
                    ),
                    "required_kopecks": (
                        daily_price_kopecks
                    ),
                    "balance_kopecks": (
                        wallet_repo.get_balance(
                            user_id
                        )
                    ),
                    "subscription_id": (
                        subscription.id
                    ),
                }

            charged = True

            new_paid_until = (
                now
                + timedelta(hours=24)
            )

            provider_user = (
                remnawave_service.ensure_user(
                    justvpn_user_id=user_id,
                    expire_at=new_paid_until,
                    hwid_device_limit=(
                        device_limit
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

            subscription.device_limit = (
                device_limit
            )

            subscription.paid_until = (
                new_paid_until
            )

            subscription.expires_at = (
                new_paid_until
            )

            subscription.billing_day_index += 1

            subscription.status = (
                SubscriptionStatus.ACTIVE
            )

            subscription_repo.update(
                subscription
            )

            logger.info(
                "Trial finished early "
                "user={} subscription={} "
                "charged={} balance={} "
                "devices={} paid_until={}",
                user_id,
                subscription.id,
                daily_price_kopecks,
                new_balance,
                device_limit,
                new_paid_until,
            )

            return {
                "status": "activated",
                "subscription_id": (
                    subscription.id
                ),
                "charged_kopecks": (
                    daily_price_kopecks
                ),
                "balance_kopecks": (
                    new_balance
                ),
                "device_limit": (
                    subscription.device_limit
                ),
                "paid_until": (
                    new_paid_until.isoformat()
                ),
            }

        except Exception:

            subscription.device_limit = (
                original_device_limit
            )

            try:
                remnawave_service.ensure_user(
                    justvpn_user_id=user_id,
                    expire_at=(
                        original_trial_ends_at
                    ),
                    hwid_device_limit=(
                        original_device_limit
                    ),
                )
            except Exception:
                logger.exception(
                    "Trial finish device limit rollback "
                    "failed user={} subscription={}",
                    user_id,
                    subscription.id,
                )

            if charged:

                try:
                    wallet_repo.credit(
                        user_id=user_id,
                        amount_kopecks=(
                            daily_price_kopecks
                        ),
                        transaction_type=(
                            "trial_finish_refund"
                        ),
                        description=(
                            f"Trial finish refund "
                            f"subscription "
                            f"#{subscription.id}"
                        ),
                    )

                except Exception:
                    logger.exception(
                        "Trial finish refund failed "
                        "user={} subscription={}",
                        user_id,
                        subscription.id,
                    )

            try:
                users_repo.restore_trial_finish(
                    user_id=user_id,
                    finished_at=now,
                    original_ends_at=(
                        original_trial_ends_at
                    ),
                )

            except Exception:
                logger.exception(
                    "Trial finish restore failed "
                    "user={}",
                    user_id,
                )

            logger.exception(
                "Trial finish failed "
                "user={} subscription={}",
                user_id,
                subscription.id,
            )

            raise


trial_service = TrialService()

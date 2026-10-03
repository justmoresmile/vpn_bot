from datetime import datetime, timedelta

from loguru import logger

from app.domain.enums.subscription_status import (
    SubscriptionStatus,
)
from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.repositories.wallet_repository import (
    wallet_repo,
)
from app.services.remnawave_service import (
    remnawave_service,
)


DAILY_PRICE_KOPECKS = 400
BILLING_PERIOD = timedelta(hours=24)


class BillingService:

    async def process_subscription(
        self,
        subscription_id: int,
    ) -> dict:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return {
                "status": "not_found",
                "subscription_id": subscription_id,
            }

        # --------------------------------------------
        # Только balance-подписки
        # --------------------------------------------

        if subscription.billing_mode != "balance":
            return {
                "status": "skipped_fixed",
                "subscription_id": subscription.id,
            }

        # --------------------------------------------
        # Deleted никогда не восстанавливаем
        # --------------------------------------------

        if (
            subscription.status
            == SubscriptionStatus.DELETED
        ):
            return {
                "status": "skipped_deleted",
                "subscription_id": subscription.id,
            }

        # --------------------------------------------
        # Администратор запретил автобиллинг
        # --------------------------------------------

        if not subscription.billing_enabled:
            return {
                "status": "skipped_disabled",
                "subscription_id": subscription.id,
            }

        now = datetime.now()

        # --------------------------------------------
        # Уже оплаченный период ещё действует
        # --------------------------------------------

        if (
            subscription.paid_until is not None
            and subscription.paid_until > now
        ):
            return {
                "status": "already_paid",
                "subscription_id": subscription.id,
                "paid_until": (
                    subscription.paid_until
                    .isoformat()
                ),
            }

        # --------------------------------------------
        # Пробуем списать 4 ₽
        # --------------------------------------------

        new_balance = wallet_repo.debit(
            user_id=subscription.user_id,
            amount_kopecks=DAILY_PRICE_KOPECKS,
            transaction_type="daily_charge",
            description=(
                f"VPN daily charge "
                f"subscription #{subscription.id}"
            ),
        )

        # --------------------------------------------
        # Денег недостаточно
        # --------------------------------------------

        if new_balance is None:

            remote = remnawave_service.get_user(
                subscription.user_id
            )

            remote_status = (
                str(remote.get("status", "")).upper()
                if remote
                else ""
            )

            if remote_status != "DISABLED":
                remnawave_service.disable_user(
                    subscription.user_id
                )

            subscription.status = (
                SubscriptionStatus.DISABLED
            )

            subscription_repo.update(
                subscription
            )

            logger.info(
                "Balance billing disabled "
                "subscription={} user={} "
                "reason=insufficient_balance",
                subscription.id,
                subscription.user_id,
            )

            return {
                "status": "insufficient_balance",
                "subscription_id": subscription.id,
                "balance_kopecks": (
                    wallet_repo.get_balance(
                        subscription.user_id
                    )
                ),
            }

        # --------------------------------------------
        # Следующие 24 часа оплачены
        # --------------------------------------------

        new_paid_until = (
            now + BILLING_PERIOD
        )

        try:

            # Устанавливаем точную дату окончания
            # в Remnawave.
            remnawave_service.ensure_user(
                justvpn_user_id=subscription.user_id,
                expire_at=new_paid_until,
                hwid_device_limit=(
                    subscription.device_limit
                ),
            )

            remote = remnawave_service.get_user(
                subscription.user_id
            )

            remote_status = (
                str(remote.get("status", "")).upper()
                if remote
                else ""
            )

            if remote_status != "ACTIVE":
                remnawave_service.enable_user(
                    subscription.user_id
                )

        except Exception:

            # Если провайдер не смог дать доступ,
            # возвращаем пользователю деньги.
            wallet_repo.credit(
                user_id=subscription.user_id,
                amount_kopecks=DAILY_PRICE_KOPECKS,
                transaction_type="billing_refund",
                description=(
                    f"Billing refund "
                    f"subscription #{subscription.id}"
                ),
            )

            logger.exception(
                "Billing provider update failed "
                "subscription={} user={}",
                subscription.id,
                subscription.user_id,
            )

            raise

        subscription.paid_until = (
            new_paid_until
        )

        # Для совместимости с существующим кодом
        # expires_at держим равным paid_until.
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
            "Balance billing charged "
            "subscription={} user={} "
            "amount={} balance={} paid_until={}",
            subscription.id,
            subscription.user_id,
            DAILY_PRICE_KOPECKS,
            new_balance,
            new_paid_until,
        )

        return {
            "status": "charged",
            "subscription_id": subscription.id,
            "charged_kopecks": (
                DAILY_PRICE_KOPECKS
            ),
            "balance_kopecks": new_balance,
            "paid_until": (
                new_paid_until.isoformat()
            ),
            "billing_day_index": (
                subscription.billing_day_index
            ),
        }

    async def process_due(
        self,
    ) -> dict:

        subscriptions = (
            subscription_repo.get_all()
        )

        processed = 0
        charged = 0
        insufficient = 0
        skipped = 0
        errors = 0

        for subscription in subscriptions:

            if subscription.billing_mode != "balance":
                continue

            if (
                subscription.status
                == SubscriptionStatus.DELETED
            ):
                continue

            if not subscription.billing_enabled:
                continue

            processed += 1

            try:

                result = await self.process_subscription(
                    subscription.id
                )

                status = result.get("status")

                if status == "charged":
                    charged += 1

                elif status == "insufficient_balance":
                    insufficient += 1

                else:
                    skipped += 1

            except Exception:

                errors += 1

                logger.exception(
                    "Balance billing failed "
                    "subscription={}",
                    subscription.id,
                )

        return {
            "processed": processed,
            "charged": charged,
            "insufficient_balance": insufficient,
            "skipped": skipped,
            "errors": errors,
        }


billing_service = BillingService()

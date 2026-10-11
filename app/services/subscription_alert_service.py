from datetime import datetime, timedelta
from math import ceil

from loguru import logger

from app.database.database import db
from app.domain.enums.subscription_status import (
    SubscriptionStatus,
)
from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.repositories.user_repository import (
    users_repo,
)
from app.repositories.wallet_repository import (
    wallet_repo,
)
from app.services.pricing_service import (
    get_daily_price_kopecks,
)
from app.services.user_notification_service import (
    user_notification_service,
)


class SubscriptionAlertService:

    # ========================================================
    # BALANCE CYCLE
    # ========================================================

    def _get_balance_cycle(
        self,
        user_id: int,
    ) -> int:

        """
        Последнее положительное движение баланса.

        После нового пополнения ID изменится и пользователь
        снова сможет получить уведомления 7/5/3/1 дней.
        """

        row = db.fetchone(
            """
            SELECT COALESCE(MAX(id), 0) AS id
            FROM wallet_transactions
            WHERE user_id = ?
              AND amount_kopecks > 0
            """,
            (
                user_id,
            ),
        )

        if row is None:
            return 0

        return int(
            row["id"] or 0
        )

    # ========================================================
    # TRIAL
    # ========================================================

    async def _check_trial(
        self,
        user,
        now: datetime,
    ) -> bool:

        if not user.trial_used:
            return False

        if user.trial_ends_at is None:
            return False

        remaining = (
            user.trial_ends_at - now
        )

        if not (
            timedelta(0)
            < remaining
            <= timedelta(hours=24)
        ):
            return False

        event_key = (
            f"trial_24h:"
            f"user:{user.id}:"
            f"ends:{int(user.trial_ends_at.timestamp())}"
        )

        await user_notification_service.send_once(
            user_id=user.id,
            event_key=event_key,
            notification_type="trial_24h",
            title="⏳ Пробный период заканчивается",
            message=(
                "До окончания бесплатного периода "
                "осталось меньше 24 часов.\n\n"
                "Пополните баланс заранее, чтобы VPN "
                "продолжил работать без перерыва."
            ),
            related_type="trial",
            related_id=user.id,
        )

        return True

    # ========================================================
    # BALANCE
    # ========================================================

    async def _check_balance(
        self,
        *,
        subscription,
        user,
        now: datetime,
    ) -> bool:

        device_limit = int(
            subscription.device_limit or 1
        )

        daily_price_kopecks = (
            get_daily_price_kopecks(
                device_limit
            )
        )

        balance_kopecks = int(
            wallet_repo.get_balance(
                user.id
            )
            or 0
        )

        balance_cycle = (
            self._get_balance_cycle(
                user.id
            )
        )

        # ----------------------------------------------------
        # VPN УЖЕ ОТКЛЮЧЁН ИЗ-ЗА БАЛАНСА
        # ----------------------------------------------------

        if (
            subscription.status
            == SubscriptionStatus.DISABLED
            and balance_kopecks
            < daily_price_kopecks
        ):

            paid_until = (
                subscription.paid_until
            )

            if (
                paid_until is None
                or paid_until <= now
            ):

                event_key = (
                    f"balance_disabled:"
                    f"subscription:{subscription.id}:"
                    f"cycle:{balance_cycle}"
                )

                await (
                    user_notification_service
                    .send_once(
                        user_id=user.id,
                        event_key=event_key,
                        notification_type=(
                            "subscription_disabled"
                        ),
                        title="⛔ VPN приостановлен",
                        message=(
                            "На балансе недостаточно средств "
                            "для оплаты следующего дня.\n\n"
                            "VPN временно приостановлен. "
                            "Пополните баланс, чтобы снова "
                            "продолжить пользоваться JustVPN."
                        ),
                        related_type="subscription",
                        related_id=subscription.id,
                    )
                )

                return True

        # Для остальных отключённых подписок ничего не шлём.
        if (
            subscription.status
            != SubscriptionStatus.ACTIVE
        ):
            return False

        # ----------------------------------------------------
        # УЖЕ НЕ ХВАТАЕТ НА СЛЕДУЮЩЕЕ СПИСАНИЕ
        # ----------------------------------------------------

        if (
            balance_kopecks
            < daily_price_kopecks
        ):

            event_key = (
                f"balance_insufficient:"
                f"subscription:{subscription.id}:"
                f"cycle:{balance_cycle}"
            )

            await (
                user_notification_service
                .send_once(
                    user_id=user.id,
                    event_key=event_key,
                    notification_type=(
                        "insufficient_balance"
                    ),
                    title="⚠️ Недостаточно средств",
                    message=(
                        "Текущего баланса уже недостаточно "
                        "для следующего суточного списания.\n\n"
                        "Пополните баланс заранее, чтобы "
                        "VPN не был приостановлен."
                    ),
                    related_type="subscription",
                    related_id=subscription.id,
                )
            )

            return True

        # ----------------------------------------------------
        # СКОЛЬКО ПОЛНЫХ/ЧАСТИЧНЫХ ДНЕЙ ОСТАЛОСЬ
        # ----------------------------------------------------

        days_left = ceil(
            balance_kopecks
            / daily_price_kopecks
        )

        if days_left not in {
            7,
            5,
            3,
            1,
        }:
            return False

        if days_left == 1:
            title = (
                "⚠️ Баланс примерно на 1 день"
            )

            message = (
                "При текущем количестве устройств "
                "баланса осталось примерно на 1 день.\n\n"
                "Рекомендуем пополнить баланс, "
                "чтобы VPN продолжил работать "
                "без перерыва."
            )

        else:
            title = (
                f"💰 Баланс примерно на "
                f"{days_left} дней"
            )

            message = (
                "При текущем количестве устройств "
                f"баланса хватит примерно на "
                f"{days_left} дней работы VPN."
            )

        event_key = (
            f"balance_{days_left}d:"
            f"subscription:{subscription.id}:"
            f"cycle:{balance_cycle}"
        )

        await user_notification_service.send_once(
            user_id=user.id,
            event_key=event_key,
            notification_type=(
                f"balance_{days_left}_days"
            ),
            title=title,
            message=message,
            related_type="subscription",
            related_id=subscription.id,
        )

        return True

    # ========================================================
    # RUN
    # ========================================================

    async def run(self) -> dict:

        now = datetime.now()

        subscriptions = (
            subscription_repo.get_all()
        )

        checked = 0
        sent = 0
        errors = 0

        checked_trial_users = set()

        for subscription in subscriptions:

            if (
                subscription.billing_mode
                != "balance"
            ):
                continue

            if (
                subscription.status
                == SubscriptionStatus.DELETED
            ):
                continue

            if not subscription.billing_enabled:
                continue

            checked += 1

            try:

                user = users_repo.get_by_id(
                    subscription.user_id
                )

                if user is None:
                    continue

                # --------------------------------------------
                # TRIAL
                # --------------------------------------------

                trial_active = (
                    user.trial_used
                    and user.trial_ends_at is not None
                    and user.trial_ends_at > now
                )

                if trial_active:

                    if (
                        user.id
                        not in checked_trial_users
                    ):

                        checked_trial_users.add(
                            user.id
                        )

                        if await self._check_trial(
                            user,
                            now,
                        ):
                            sent += 1

                    # Пока идёт trial, предупреждения
                    # по платному балансу не отправляем.
                    continue

                # --------------------------------------------
                # BALANCE
                # --------------------------------------------

                if await self._check_balance(
                    subscription=subscription,
                    user=user,
                    now=now,
                ):
                    sent += 1

            except Exception:

                errors += 1

                logger.exception(
                    "Subscription alert failed "
                    "subscription={} user={}",
                    subscription.id,
                    subscription.user_id,
                )

        return {
            "checked": checked,
            "sent": sent,
            "errors": errors,
        }


subscription_alert_service = (
    SubscriptionAlertService()
)

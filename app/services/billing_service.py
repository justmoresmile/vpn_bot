from datetime import datetime, timedelta

from loguru import logger

from app.database.database import db
from app.domain.enums.subscription_status import (
    SubscriptionStatus,
)
from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.services.remnawave_service import (
    remnawave_service,
)
from app.services.pricing_service import (
    get_daily_price_kopecks,
)


BILLING_PERIOD = timedelta(hours=24)


class BillingService:

    def _atomic_charge_period(
        self,
        subscription_id: int,
    ) -> dict:

        now = datetime.now()
        now_ts = int(
            now.timestamp()
        )

        with db.transaction() as cursor:

            # ВАЖНО:
            # BEGIN IMMEDIATE уже выполнен в db.transaction().
            # Пока эта транзакция не завершится, второй writer
            # не сможет одновременно списать этот же период.

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    status,
                    device_limit,
                    expires_at,
                    billing_mode,
                    paid_until,
                    billing_day_index,
                    billing_enabled
                FROM subscriptions
                WHERE id = ?
                """,
                (
                    subscription_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                return {
                    "status": "not_found",
                    "subscription_id": (
                        subscription_id
                    ),
                }

            if row["billing_mode"] != "balance":
                return {
                    "status": "skipped_fixed",
                    "subscription_id": (
                        subscription_id
                    ),
                }

            if (
                row["status"]
                == SubscriptionStatus.DELETED
            ):
                return {
                    "status": "skipped_deleted",
                    "subscription_id": (
                        subscription_id
                    ),
                }

            if not bool(
                row["billing_enabled"]
            ):
                return {
                    "status": "skipped_disabled",
                    "subscription_id": (
                        subscription_id
                    ),
                }

            old_paid_until_ts = (
                int(row["paid_until"])
                if row["paid_until"]
                else None
            )

            # Второй параллельный billing после ожидания
            # write-lock увидит уже новый paid_until
            # и ничего больше не спишет.
            if (
                old_paid_until_ts is not None
                and old_paid_until_ts > now_ts
            ):
                return {
                    "status": "already_paid",
                    "subscription_id": (
                        subscription_id
                    ),
                    "paid_until": (
                        datetime.fromtimestamp(
                            old_paid_until_ts
                        ).isoformat()
                    ),
                }

            user_id = int(
                row["user_id"]
            )

            device_limit = int(
                row["device_limit"] or 1
            )

            daily_price_kopecks = (
                get_daily_price_kopecks(
                    device_limit
                )
            )

            cursor.execute(
                """
                SELECT balance_kopecks
                FROM users
                WHERE id = ?
                """,
                (
                    user_id,
                ),
            )

            user_row = cursor.fetchone()

            if user_row is None:
                raise ValueError(
                    "User not found"
                )

            current_balance = int(
                user_row[
                    "balance_kopecks"
                ]
            )

            if (
                current_balance
                < daily_price_kopecks
            ):

                cursor.execute(
                    """
                    UPDATE subscriptions
                    SET status = ?
                    WHERE id = ?
                    """,
                    (
                        SubscriptionStatus.DISABLED,
                        subscription_id,
                    ),
                )

                return {
                    "status": (
                        "insufficient_balance"
                    ),
                    "subscription_id": (
                        subscription_id
                    ),
                    "user_id": user_id,
                    "balance_kopecks": (
                        current_balance
                    ),
                    "device_limit": (
                        device_limit
                    ),
                }

            new_balance = (
                current_balance
                - daily_price_kopecks
            )

            new_paid_until = (
                now + BILLING_PERIOD
            )

            new_paid_until_ts = int(
                new_paid_until.timestamp()
            )

            old_expires_at_ts = (
                int(row["expires_at"])
                if row["expires_at"]
                else None
            )

            old_billing_day_index = int(
                row["billing_day_index"]
                or 0
            )

            old_status = row["status"]

            cursor.execute(
                """
                UPDATE users
                SET balance_kopecks = ?
                WHERE id = ?
                """,
                (
                    new_balance,
                    user_id,
                ),
            )

            cursor.execute(
                """
                INSERT INTO wallet_transactions
                (
                    user_id,
                    type,
                    amount_kopecks,
                    balance_after_kopecks,
                    payment_id,
                    description,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    "daily_charge",
                    -daily_price_kopecks,
                    new_balance,
                    None,
                    (
                        f"VPN daily charge "
                        f"subscription "
                        f"#{subscription_id} "
                        f"devices={device_limit}"
                    ),
                    now_ts,
                ),
            )

            cursor.execute(
                """
                UPDATE subscriptions
                SET
                    paid_until = ?,
                    expires_at = ?,
                    billing_day_index =
                        billing_day_index + 1,
                    status = ?
                WHERE id = ?
                """,
                (
                    new_paid_until_ts,
                    new_paid_until_ts,
                    SubscriptionStatus.ACTIVE,
                    subscription_id,
                ),
            )

            return {
                "status": "charged",
                "subscription_id": (
                    subscription_id
                ),
                "user_id": user_id,
                "device_limit": (
                    device_limit
                ),
                "charged_kopecks": (
                    daily_price_kopecks
                ),
                "balance_kopecks": (
                    new_balance
                ),
                "paid_until": (
                    new_paid_until
                ),
                "new_paid_until_ts": (
                    new_paid_until_ts
                ),
                "old_paid_until_ts": (
                    old_paid_until_ts
                ),
                "old_expires_at_ts": (
                    old_expires_at_ts
                ),
                "old_billing_day_index": (
                    old_billing_day_index
                ),
                "old_status": (
                    old_status
                ),
            }


    def _rollback_atomic_charge(
        self,
        charge: dict,
    ) -> None:

        subscription_id = int(
            charge["subscription_id"]
        )

        user_id = int(
            charge["user_id"]
        )

        amount_kopecks = int(
            charge["charged_kopecks"]
        )

        expected_paid_until = int(
            charge["new_paid_until_ts"]
        )

        with db.transaction() as cursor:

            # Откатываем только именно НАШ claim.
            # Если состояние уже изменилось кем-то ещё,
            # чужие данные не трогаем.
            cursor.execute(
                """
                SELECT
                    paid_until,
                    billing_day_index
                FROM subscriptions
                WHERE id = ?
                """,
                (
                    subscription_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                return

            current_paid_until = (
                int(row["paid_until"])
                if row["paid_until"]
                else None
            )

            expected_day_index = (
                int(
                    charge[
                        "old_billing_day_index"
                    ]
                )
                + 1
            )

            if (
                current_paid_until
                != expected_paid_until
                or int(
                    row["billing_day_index"]
                    or 0
                )
                != expected_day_index
            ):
                logger.error(
                    "Billing rollback skipped "
                    "because subscription changed "
                    "subscription={}",
                    subscription_id,
                )
                return

            cursor.execute(
                """
                SELECT balance_kopecks
                FROM users
                WHERE id = ?
                """,
                (
                    user_id,
                ),
            )

            user_row = cursor.fetchone()

            if user_row is None:
                raise ValueError(
                    "User not found"
                )

            refunded_balance = (
                int(
                    user_row[
                        "balance_kopecks"
                    ]
                )
                + amount_kopecks
            )

            cursor.execute(
                """
                UPDATE users
                SET balance_kopecks = ?
                WHERE id = ?
                """,
                (
                    refunded_balance,
                    user_id,
                ),
            )

            cursor.execute(
                """
                INSERT INTO wallet_transactions
                (
                    user_id,
                    type,
                    amount_kopecks,
                    balance_after_kopecks,
                    payment_id,
                    description,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    "billing_refund",
                    amount_kopecks,
                    refunded_balance,
                    None,
                    (
                        f"Billing refund "
                        f"subscription "
                        f"#{subscription_id}"
                    ),
                    int(
                        datetime.now().timestamp()
                    ),
                ),
            )

            cursor.execute(
                """
                UPDATE subscriptions
                SET
                    paid_until = ?,
                    expires_at = ?,
                    billing_day_index = ?,
                    status = ?
                WHERE id = ?
                """,
                (
                    charge[
                        "old_paid_until_ts"
                    ],
                    charge[
                        "old_expires_at_ts"
                    ],
                    charge[
                        "old_billing_day_index"
                    ],
                    charge[
                        "old_status"
                    ],
                    subscription_id,
                ),
            )


    async def process_subscription(
        self,
        subscription_id: int,
    ) -> dict:

        # --------------------------------------------------
        # Атомарно:
        # - проверяем paid_until
        # - проверяем баланс
        # - списываем деньги
        # - пишем transaction
        # - продлеваем подписку
        #
        # Всё это происходит под BEGIN IMMEDIATE.
        # --------------------------------------------------

        charge = self._atomic_charge_period(
            subscription_id
        )

        status = charge.get(
            "status"
        )

        # --------------------------------------------------
        # Недостаточно средств
        # --------------------------------------------------

        if status == "insufficient_balance":

            user_id = int(
                charge["user_id"]
            )

            remote = (
                remnawave_service.get_user(
                    user_id
                )
            )

            remote_status = (
                str(
                    remote.get(
                        "status",
                        "",
                    )
                ).upper()
                if remote
                else ""
            )

            if remote_status != "DISABLED":
                remnawave_service.disable_user(
                    user_id
                )

            logger.info(
                "Balance billing disabled "
                "subscription={} user={} "
                "reason=insufficient_balance",
                subscription_id,
                user_id,
            )

            return charge

        # --------------------------------------------------
        # Ничего списывать не нужно
        # --------------------------------------------------

        if status != "charged":
            return charge

        user_id = int(
            charge["user_id"]
        )

        device_limit = int(
            charge["device_limit"]
        )

        daily_price_kopecks = int(
            charge["charged_kopecks"]
        )

        new_balance = int(
            charge["balance_kopecks"]
        )

        new_paid_until = (
            charge["paid_until"]
        )

        # --------------------------------------------------
        # После успешного DB claim обновляем Remnawave.
        #
        # Сетевой запрос специально НЕ держим внутри
        # SQLite transaction.
        # --------------------------------------------------

        try:

            remnawave_service.ensure_user(
                justvpn_user_id=user_id,
                expire_at=new_paid_until,
                hwid_device_limit=(
                    device_limit
                ),
            )

            remote = (
                remnawave_service.get_user(
                    user_id
                )
            )

            remote_status = (
                str(
                    remote.get(
                        "status",
                        "",
                    )
                ).upper()
                if remote
                else ""
            )

            if remote_status != "ACTIVE":
                remnawave_service.enable_user(
                    user_id
                )

        except Exception:

            # Remnawave не выдал доступ.
            # Возвращаем БД и баланс в состояние,
            # которое было до этого списания.
            try:

                self._rollback_atomic_charge(
                    charge
                )

            except Exception:

                logger.exception(
                    "CRITICAL billing rollback "
                    "failed subscription={} user={}",
                    subscription_id,
                    user_id,
                )

            logger.exception(
                "Billing provider update failed "
                "subscription={} user={}",
                subscription_id,
                user_id,
            )

            raise

        billing_day_index = (
            int(
                charge[
                    "old_billing_day_index"
                ]
            )
            + 1
        )

        logger.info(
            "Balance billing charged "
            "subscription={} user={} "
            "amount={} balance={} "
            "paid_until={}",
            subscription_id,
            user_id,
            daily_price_kopecks,
            new_balance,
            new_paid_until,
        )

        return {
            "status": "charged",
            "subscription_id": (
                subscription_id
            ),
            "charged_kopecks": (
                daily_price_kopecks
            ),
            "device_limit": (
                device_limit
            ),
            "balance_kopecks": (
                new_balance
            ),
            "paid_until": (
                new_paid_until.isoformat()
            ),
            "billing_day_index": (
                billing_day_index
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

from datetime import datetime

from app.database.database import db
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.subscription import Subscription


class SubscriptionRepository:

    @staticmethod
    def _to_entity(
        row,
    ) -> Subscription:

        return Subscription(
            id=row["id"],
            user_id=row["user_id"],
            protocol=row["protocol"],
            provider=(
                row["provider"]
                if "provider" in row.keys()
                else "remnawave"
            ),
            server_id=row["server_id"],
            inbound_id=row["inbound_id"],
            client_id=row["client_uuid"],
            client_email=row["client_email"],
            sub_id=(
                row["sub_id"]
                if "sub_id" in row.keys()
                else None
            ),
            subscription_token=(
                row["subscription_token"]
                if "subscription_token" in row.keys()
                else None
            ),
            config=row["config"],
            status=SubscriptionStatus(
                row["status"]
            ),
            device_limit=(
                row["device_limit"]
                if "device_limit" in row.keys()
                else 1
            ),
            device_limit_locked_until=(
                datetime.fromtimestamp(
                    row["device_limit_locked_until"]
                )
                if (
                    "device_limit_locked_until" in row.keys()
                    and row["device_limit_locked_until"]
                )
                else None
            ),
            created_at=datetime.fromtimestamp(
                row["created_at"]
            ),
            expires_at=datetime.fromtimestamp(
                row["expires_at"]
            ),
            billing_mode=(
                row["billing_mode"]
                if "billing_mode" in row.keys()
                else "fixed"
            ),
            paid_until=(
                datetime.fromtimestamp(
                    row["paid_until"]
                )
                if (
                    "paid_until" in row.keys()
                    and row["paid_until"]
                )
                else None
            ),
            billing_day_index=(
                row["billing_day_index"]
                if "billing_day_index" in row.keys()
                else 0
            ),
            billing_enabled=(
                bool(row["billing_enabled"])
                if "billing_enabled" in row.keys()
                else True
            ),
        )

    @staticmethod
    def create(
        subscription: Subscription,
    ) -> Subscription:

        db.execute(
            """
            INSERT INTO subscriptions
            (
                user_id,
                provider,
                server_id,
                protocol,
                inbound_id,
                client_uuid,
                client_email,
                sub_id,
                subscription_token,
                config,
                status,
                device_limit,
                created_at,
                expires_at,
                billing_mode,
                paid_until,
                billing_day_index,
                billing_enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription.user_id,
                subscription.provider,
                subscription.server_id,
                subscription.protocol,
                subscription.inbound_id,
                subscription.client_id,
                subscription.client_email,
                subscription.sub_id,
                subscription.subscription_token,
                subscription.config,
                subscription.status,
                subscription.device_limit,
                int(
                    subscription.created_at.timestamp()
                ),
                int(
                    subscription.expires_at.timestamp()
                ),
                subscription.billing_mode,
                (
                    int(
                        subscription.paid_until.timestamp()
                    )
                    if subscription.paid_until
                    else None
                ),
                subscription.billing_day_index,
                int(subscription.billing_enabled),
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE id = last_insert_rowid()
            """
        )

        return SubscriptionRepository._to_entity(
            row
        )

    @staticmethod
    def get_by_id(
        subscription_id: int,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE id = ?
            """,
            (
                subscription_id,
            ),
        )

        if row is None:
            return None

        return SubscriptionRepository._to_entity(
            row
        )

    @staticmethod
    def get_by_user(
        user_id: int,
    ) -> list[Subscription]:

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            WHERE user_id = ?
            AND status != ?
            ORDER BY created_at DESC
            """,
            (
                user_id,
                SubscriptionStatus.DELETED,
            ),
        )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def get_active_by_user(
        user_id: int,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE user_id = ?
              AND status = ?
            ORDER BY expires_at DESC
            LIMIT 1
            """,
            (
                user_id,
                SubscriptionStatus.ACTIVE,
            ),
        )

        if row is None:
            return None

        return SubscriptionRepository._to_entity(
            row
        )

    @staticmethod
    def get_active_by_user_protocol(
        user_id: int,
        protocol: str,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE user_id = ?
            AND protocol = ?
            AND status = ?
            ORDER BY expires_at DESC
            LIMIT 1
            """,
            (
                user_id,
                protocol,
                SubscriptionStatus.ACTIVE,
            ),
        )

        if row is None:
            return None

        return SubscriptionRepository._to_entity(
            row
        )

    @staticmethod
    def get_active(
    ) -> list[Subscription]:

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            WHERE status = ?
            ORDER BY expires_at
            """,
            (
                SubscriptionStatus.ACTIVE,
            ),
        )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def get_latest_by_user(
        user_id: int,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE user_id = ?
            AND status != ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (
                user_id,
                SubscriptionStatus.DELETED,
            ),
        )

        if row is None:
            return None

        return SubscriptionRepository._to_entity(
            row
        )

    @staticmethod
    def get_expired_active(
    ) -> list[Subscription]:

        now = int(
            datetime.now().timestamp()
        )

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            WHERE status = ?
              AND expires_at <= ?
            """,
            (
                SubscriptionStatus.ACTIVE,
                now,
            ),
        )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def get_expiring(
        days: int,
    ) -> list[Subscription]:

        now = int(
            datetime.now().timestamp()
        )

        future = int(
            datetime.now().timestamp()
            + days * 86400
        )

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            WHERE status = ?
              AND expires_at > ?
              AND expires_at <= ?
            """,
            (
                SubscriptionStatus.ACTIVE,
                now,
                future,
            ),
        )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def update(
        subscription: Subscription,
    ):

        db.execute(
            """
            UPDATE subscriptions
            SET
                provider = ?,
                protocol = ?,
                server_id = ?,
                inbound_id = ?,
                client_uuid = ?,
                client_email = ?,
                sub_id = ?,
                subscription_token = ?,
                config = ?,
                status = ?,
                device_limit = ?,
                device_limit_locked_until = ?,
                expires_at = ?,
                billing_mode = ?,
                paid_until = ?,
                billing_day_index = ?,
                billing_enabled = ?
            WHERE id = ?
            """,
            (
                subscription.provider,
                subscription.protocol,
                subscription.server_id,
                subscription.inbound_id,
                subscription.client_id,
                subscription.client_email,
                subscription.sub_id,
                subscription.subscription_token,
                subscription.config,
                subscription.status,
                subscription.device_limit,
                (
                    int(
                        subscription.device_limit_locked_until.timestamp()
                    )
                    if subscription.device_limit_locked_until
                    else None
                ),
                int(
                    subscription.expires_at.timestamp()
                ),
                subscription.billing_mode,
                (
                    int(
                        subscription.paid_until.timestamp()
                    )
                    if subscription.paid_until
                    else None
                ),
                subscription.billing_day_index,
                int(subscription.billing_enabled),
                subscription.id,
            ),
        )

    @staticmethod
    def delete(
        subscription_id: int,
    ):

        db.execute(
            """
            UPDATE subscriptions
            SET status = ?
            WHERE id = ?
            """,
            (
                SubscriptionStatus.DELETED,
                subscription_id,
            ),
        )

    @staticmethod
    def get_all(
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Subscription]:

        if limit is None:

            rows = db.fetchall(
                """
                SELECT *
                FROM subscriptions
                ORDER BY id DESC
                """
            )

        else:

            rows = db.fetchall(
                """
                SELECT *
                FROM subscriptions
                ORDER BY id DESC
                LIMIT ?
                OFFSET ?
                """,
                (
                    limit,
                    offset,
                ),
            )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def count() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            """
        )

        return row["total"]

    @staticmethod
    def count_active() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            WHERE status = ?
            """,
            (
                SubscriptionStatus.ACTIVE,
            ),
        )

        return row["total"]

    @staticmethod
    def count_expired() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            WHERE status = ?
            """,
            (
                SubscriptionStatus.EXPIRED,
            ),
        )

        return row["total"]

    @staticmethod
    def count_active_by_server(
        server_id: int,
    ) -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            WHERE server_id = ?
            AND status = ?
            """,
            (
                server_id,
                SubscriptionStatus.ACTIVE,
            ),
        )

        return row["total"]

    @staticmethod
    def clear_notifications(
        subscription_id: int,
    ):

        db.execute(
            """
            DELETE FROM subscription_notifications
            WHERE subscription_id = ?
            """,
            (
                subscription_id,
            ),
        )

    @staticmethod
    def get_admin_subscriptions(
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Subscription], int]:

        offset = (
            page - 1
        ) * limit

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            ORDER BY id DESC
            LIMIT ?
            OFFSET ?
            """,
            (
                limit,
                offset,
            ),
        )

        subscriptions = [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            """
        )

        return (
            subscriptions,
            row["total"],
        )

    @staticmethod
    def get_by_server(
        server_id: int,
    ) -> list[Subscription]:

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            WHERE server_id = ?
            """,
            (
                server_id,
            ),
        )

        return [
            SubscriptionRepository._to_entity(
                row
            )
            for row in rows
        ]

    def count_by_server(
        self,
        server_id: int,
    ) -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*)
            FROM subscriptions
            WHERE server_id = ?
            """,
            (
                server_id,
            ),
        )

        return row[0]

    @staticmethod
    def get_by_token(
        token: str,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE subscription_token = ?
            """,
            (
                token,
            ),
        )

        if row is None:
            return None

        return SubscriptionRepository._to_entity(
            row
        )


subscription_repo = SubscriptionRepository()
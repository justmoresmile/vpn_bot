from datetime import datetime

from app.database.database import db
from app.domain.enums import SubscriptionStatus
from app.domain.subscription import Subscription


class SubscriptionRepository:

    @staticmethod
    def _to_entity(row) -> Subscription:

        return Subscription(
            id=row["id"],
            user_id=row["user_id"],
            protocol=row["protocol"],
            inbound_id=row["inbound_id"],
            client_id=row["client_uuid"],
            client_email=row["client_email"],
            sub_id=(
                row["sub_id"]
                if "sub_id" in row.keys()
                else None
            ),
            config=row["config"],
            status=SubscriptionStatus(
                row["status"]
            ),
            created_at=datetime.fromtimestamp(
                row["created_at"]
            ),
            expires_at=datetime.fromtimestamp(
                row["expires_at"]
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
                protocol,
                inbound_id,
                client_uuid,
                client_email,
                sub_id,
                config,
                status,
                created_at,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription.user_id,
                subscription.protocol,
                subscription.inbound_id,
                subscription.client_id,
                subscription.client_email,
                subscription.sub_id,
                subscription.config,
                subscription.status,
                int(subscription.created_at.timestamp()),
                int(subscription.expires_at.timestamp()),
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
            (subscription_id,),
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
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

        return [
            SubscriptionRepository._to_entity(row)
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

        return SubscriptionRepository._to_entity(row)

    @staticmethod
    def get_latest_by_user(
        user_id: int,
    ) -> Subscription | None:

        row = db.fetchone(
            """
            SELECT *
            FROM subscriptions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
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
            SubscriptionRepository._to_entity(row)
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
                protocol=?,
                inbound_id=?,
                client_uuid=?,
                client_email=?,
                sub_id=?,
                config=?,
                status=?,
                expires_at=?
            WHERE id=?
            """,
            (
                subscription.protocol,
                subscription.inbound_id,
                subscription.client_id,
                subscription.client_email,
                subscription.sub_id,
                subscription.config,
                subscription.status,
                int(subscription.expires_at.timestamp()),
                subscription.id,
            ),
        )

    @staticmethod
    def delete(
        subscription_id: int,
    ):

        db.execute(
            """
            DELETE FROM subscriptions
            WHERE id=?
            """,
            (subscription_id,),
        )

    @staticmethod
    def get_all(
    ) -> list[Subscription]:

        rows = db.fetchall(
            """
            SELECT *
            FROM subscriptions
            """
        )

        return [
            SubscriptionRepository._to_entity(row)
            for row in rows
        ]


subscription_repo = SubscriptionRepository()
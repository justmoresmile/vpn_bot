from datetime import datetime

from app.database.database import db
from app.domain.legacy_enums import SubscriptionStatus
from app.domain.subscription import Subscription


class SubscriptionRepository:

    @staticmethod
    def _to_entity(row) -> Subscription:

        return Subscription(
            id=row["id"],
            user_id=row["user_id"],
            server_id=row["server_id"],
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
                server_id,
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription.user_id,
                subscription.server_id,
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
            AND status != ?
            ORDER BY created_at DESC
            """,
            (
                user_id,
                SubscriptionStatus.DELETED,
            ),
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
            SubscriptionRepository._to_entity(row)
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

        return SubscriptionRepository._to_entity(row)
        
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
    def get_expiring(
        days: int,
    ) -> list[Subscription]:

        now = int(
            datetime.now().timestamp()
        )

        future = int(
            (
                datetime.now()
                .timestamp()
                +
                days * 86400
            )
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
                server_id=?,
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
                subscription.server_id,
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
            SubscriptionRepository._to_entity(row)
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

        offset = (page - 1) * limit

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
            SubscriptionRepository._to_entity(row)
            for row in rows
        ]

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM subscriptions
            """
        )

        return subscriptions, row["total"]


subscription_repo = SubscriptionRepository()
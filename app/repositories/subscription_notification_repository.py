from datetime import datetime

from app.database.database import db


class SubscriptionNotificationRepository:


    @staticmethod
    def delete_by_subscription(
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
    def exists(
        subscription_id: int,
        notification_type: str,
    ) -> bool:


        row = db.fetchone(
            """
            SELECT id
            FROM subscription_notifications
            WHERE subscription_id = ?
            AND notification_type = ?
            """,
            (
                subscription_id,
                notification_type,
            ),
        )


        return row is not None



    @staticmethod
    def create(
        subscription_id: int,
        notification_type: str,
    ):


        db.execute(
            """
            INSERT OR IGNORE INTO
            subscription_notifications
            (
                subscription_id,
                notification_type,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                subscription_id,
                notification_type,
                int(
                    datetime.now().timestamp()
                ),
            ),
        )



subscription_notification_repo = (
    SubscriptionNotificationRepository()
)
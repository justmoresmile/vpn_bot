from app.database.database import db


class NotificationRepository:

    def create(
        self,
        *,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> int:

        db.execute(
            """
            INSERT INTO notifications (
                user_id,
                type,
                title,
                message,
                related_type,
                related_id,
                is_read
            )
            VALUES (?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                notification_type,
                title,
                message,
                related_type,
                related_id,
            ),
        )

        row = db.fetchone(
            """
            SELECT id
            FROM notifications
            WHERE id = last_insert_rowid()
            """
        )

        if row is None:
            raise RuntimeError(
                "Failed to create notification"
            )

        return row["id"]

    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 100,
    ):

        return db.fetchall(
            """
            SELECT *
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

    def unread_count(
        self,
        user_id: int,
    ) -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS count
            FROM notifications
            WHERE user_id = ?
              AND is_read = 0
            """,
            (
                user_id,
            ),
        )

        return int(
            row["count"] if row else 0
        )

    def delete_by_related(
        self,
        *,
        user_id: int,
        related_type: str,
        related_id: int,
    ) -> None:

        db.execute(
            """
            DELETE FROM notifications
            WHERE user_id = ?
              AND related_type = ?
              AND related_id = ?
            """,
            (
                user_id,
                related_type,
                related_id,
            ),
        )


    def mark_read(
        self,
        *,
        user_id: int,
        notification_id: int,
    ) -> None:

        db.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE id = ?
              AND user_id = ?
            """,
            (
                notification_id,
                user_id,
            ),
        )

    def mark_all_read(
        self,
        user_id: int,
    ) -> None:

        db.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = ?
              AND is_read = 0
            """,
            (
                user_id,
            ),
        )


    def create_event(
        self,
        *,
        user_id: int,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ):

        db.execute(
            """
            INSERT OR IGNORE INTO notifications (
                user_id,
                type,
                title,
                message,
                related_type,
                related_id,
                is_read,
                event_key,
                telegram_sent
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, 0)
            """,
            (
                user_id,
                notification_type,
                title,
                message,
                related_type,
                related_id,
                event_key,
            ),
        )

        return db.fetchone(
            """
            SELECT *
            FROM notifications
            WHERE event_key = ?
            """,
            (
                event_key,
            ),
        )


    def mark_telegram_sent(
        self,
        notification_id: int,
    ) -> None:

        db.execute(
            """
            UPDATE notifications
            SET telegram_sent = 1
            WHERE id = ?
            """,
            (
                notification_id,
            ),
        )


notification_repo = NotificationRepository()

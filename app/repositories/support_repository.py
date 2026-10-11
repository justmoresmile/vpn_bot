from datetime import datetime

from app.database.database import db

from app.domain.support import (
    SupportTicket,
    SupportMessage,
)


class SupportRepository:

    # ==========================================================
    # MAPPERS
    # ==========================================================

    @staticmethod
    def _ticket_to_entity(
        row,
    ) -> SupportTicket:

        return SupportTicket(
            id=row["id"],
            user_id=row["user_id"],
            subject=row["subject"],
            category=row["category"],
            status=row["status"],
            created_at=datetime.fromtimestamp(
                row["created_at"]
            ),
            updated_at=datetime.fromtimestamp(
                row["updated_at"]
            ),
            closed_at=(
                datetime.fromtimestamp(
                    row["closed_at"]
                )
                if row["closed_at"]
                else None
            ),
            telegram_thread_id=(
                row["telegram_thread_id"]
                if "telegram_thread_id"
                in row.keys()
                else None
            ),
        )

    @staticmethod
    def _message_to_entity(
        row,
    ) -> SupportMessage:

        return SupportMessage(
            id=row["id"],
            ticket_id=row["ticket_id"],
            sender_type=row["sender_type"],
            sender_id=row["sender_id"],
            message=row["message"],
            is_read=bool(
                row["is_read"]
            ),
            created_at=datetime.fromtimestamp(
                row["created_at"]
            ),
        )

    # ==========================================================
    # TICKETS
    # ==========================================================

    @staticmethod
    def create_ticket(
        *,
        user_id: int,
        subject: str,
        category: str | None = None,
    ) -> SupportTicket:

        now = int(
            datetime.now().timestamp()
        )

        db.execute(
            """
            INSERT INTO support_tickets
            (
                user_id,
                subject,
                category,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, 'open', ?, ?)
            """,
            (
                user_id,
                subject,
                category,
                now,
                now,
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM support_tickets
            WHERE id = last_insert_rowid()
            """
        )

        if row is None:
            raise RuntimeError(
                "Failed to create support ticket"
            )

        return SupportRepository._ticket_to_entity(
            row
        )

    @staticmethod
    def get_ticket(
        ticket_id: int,
    ) -> SupportTicket | None:

        row = db.fetchone(
            """
            SELECT *
            FROM support_tickets
            WHERE id = ?
            """,
            (
                ticket_id,
            ),
        )

        if row is None:
            return None

        return SupportRepository._ticket_to_entity(
            row
        )

    @staticmethod
    def get_user_tickets(
        user_id: int,
    ) -> list[SupportTicket]:

        rows = db.fetchall(
            """
            SELECT *
            FROM support_tickets
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (
                user_id,
            ),
        )

        return [
            SupportRepository._ticket_to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def get_open_tickets(
    ) -> list[SupportTicket]:

        rows = db.fetchall(
            """
            SELECT *
            FROM support_tickets
            WHERE status != 'closed'
            ORDER BY updated_at DESC
            """
        )

        return [
            SupportRepository._ticket_to_entity(
                row
            )
            for row in rows
        ]

    @staticmethod
    def update_status(
        ticket_id: int,
        status: str,
    ) -> None:

        now = int(
            datetime.now().timestamp()
        )

        closed_at = (
            now
            if status == "closed"
            else None
        )

        db.execute(
            """
            UPDATE support_tickets
            SET
                status = ?,
                updated_at = ?,
                closed_at = ?
            WHERE id = ?
            """,
            (
                status,
                now,
                closed_at,
                ticket_id,
            ),
        )

    @staticmethod
    def set_telegram_thread_id(
        ticket_id: int,
        thread_id: int,
    ) -> None:

        db.execute(
            """
            UPDATE support_tickets
            SET telegram_thread_id = ?
            WHERE id = ?
            """,
            (
                thread_id,
                ticket_id,
            ),
        )


    @staticmethod
    def get_by_telegram_thread_id(
        thread_id: int,
    ) -> SupportTicket | None:

        row = db.fetchone(
            """
            SELECT *
            FROM support_tickets
            WHERE telegram_thread_id = ?
            """,
            (
                thread_id,
            ),
        )

        if row is None:
            return None

        return SupportRepository._ticket_to_entity(
            row
        )


    @staticmethod
    def delete_ticket(
        ticket_id: int,
    ) -> None:

        db.execute(
            """
            DELETE FROM support_messages
            WHERE ticket_id = ?
            """,
            (
                ticket_id,
            ),
        )

        db.execute(
            """
            DELETE FROM support_tickets
            WHERE id = ?
            """,
            (
                ticket_id,
            ),
        )


    # ==========================================================
    # MESSAGES
    # ==========================================================

    @staticmethod
    def create_message(
        *,
        ticket_id: int,
        sender_type: str,
        sender_id: int | None,
        message: str,
        is_read: bool = False,
    ) -> SupportMessage:

        now = int(
            datetime.now().timestamp()
        )

        db.execute(
            """
            INSERT INTO support_messages
            (
                ticket_id,
                sender_type,
                sender_id,
                message,
                is_read,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                sender_type,
                sender_id,
                message,
                int(is_read),
                now,
            ),
        )

        db.execute(
            """
            UPDATE support_tickets
            SET updated_at = ?
            WHERE id = ?
            """,
            (
                now,
                ticket_id,
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM support_messages
            WHERE id = last_insert_rowid()
            """
        )

        if row is None:
            raise RuntimeError(
                "Failed to create support message"
            )

        return SupportRepository._message_to_entity(
            row
        )

    @staticmethod
    def get_messages(
        ticket_id: int,
    ) -> list[SupportMessage]:

        rows = db.fetchall(
            """
            SELECT *
            FROM support_messages
            WHERE ticket_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (
                ticket_id,
            ),
        )

        return [
            SupportRepository._message_to_entity(
                row
            )
            for row in rows
        ]


support_repo = SupportRepository()

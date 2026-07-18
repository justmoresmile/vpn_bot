from datetime import datetime

from app.database.database import db
from app.domain.payment import Payment


class PaymentRepository:

    @staticmethod
    def _to_entity(row) -> Payment:
        return Payment(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            currency=row["currency"],
            provider=row["provider"],
            status=row["status"],
            created_at=datetime.fromtimestamp(row["created_at"]),
        )

    @staticmethod
    def create(payment: Payment) -> Payment:
        db.execute(
            """
            INSERT INTO payments
            (
                user_id,
                amount,
                currency,
                provider,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payment.user_id,
                payment.amount,
                payment.currency,
                payment.provider,
                payment.status,
                int(payment.created_at.timestamp()),
            ),
        )

        row = db.fetchone(
            """
            SELECT *
            FROM payments
            WHERE id = last_insert_rowid()
            """
        )

        return PaymentRepository._to_entity(row)

    @staticmethod
    def get_by_id(payment_id: int) -> Payment | None:
        row = db.fetchone(
            """
            SELECT *
            FROM payments
            WHERE id = ?
            """,
            (payment_id,),
        )

        return PaymentRepository._to_entity(row) if row else None

    @staticmethod
    def get_by_user(user_id: int) -> list[Payment]:
        rows = db.fetchall(
            """
            SELECT *
            FROM payments
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

        return [PaymentRepository._to_entity(row) for row in rows]

    @staticmethod
    def update_status(payment_id: int, status: str):
        db.execute(
            """
            UPDATE payments
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                payment_id,
            ),
        )


payment_repo = PaymentRepository()
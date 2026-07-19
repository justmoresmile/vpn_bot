from datetime import datetime

from app.database.database import db
from app.domain.payment import Payment


class PaymentRepository:

    @staticmethod
    def _to_entity(row) -> Payment:

        return Payment(

            id=row["id"],

            user_id=row["user_id"],

            protocol=row["protocol"],

            subscription_days=row["subscription_days"],

            amount=row["amount"],

            currency=row["currency"],

            provider=row["provider"],

            provider_payment_id=row["provider_payment_id"],

            confirmation_url=row["confirmation_url"],

            status=row["status"],

            created_at=datetime.fromtimestamp(
                row["created_at"]
            ),

            paid_at=(
                datetime.fromtimestamp(
                    row["paid_at"]
                )
                if row["paid_at"]
                else None
            ),
        )


    @staticmethod
    def create(
        payment: Payment,
    ) -> Payment:


        db.execute(
            """
            INSERT INTO payments
            (
                user_id,

                protocol,

                subscription_days,

                amount,

                currency,

                provider,

                provider_payment_id,

                confirmation_url,

                status,

                created_at,

                paid_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                payment.user_id,

                payment.protocol,

                payment.subscription_days,

                payment.amount,

                payment.currency,

                payment.provider,

                payment.provider_payment_id,

                payment.confirmation_url,

                payment.status,

                int(
                    payment.created_at.timestamp()
                ),

                (
                    int(payment.paid_at.timestamp())
                    if payment.paid_at
                    else None
                ),
            ),
        )


        row = db.fetchone(
            """
            SELECT *

            FROM payments

            WHERE id = last_insert_rowid()

            """
        )


        return PaymentRepository._to_entity(
            row
        )


    @staticmethod
    def get_by_id(
        payment_id: int,
    ) -> Payment | None:


        row = db.fetchone(
            """
            SELECT *

            FROM payments

            WHERE id = ?

            """,

            (
                payment_id,
            ),
        )


        return (
            PaymentRepository._to_entity(row)
            if row
            else None
        )


    @staticmethod
    def get_by_provider_payment_id(
        provider_payment_id: str,
    ) -> Payment | None:


        row = db.fetchone(
            """
            SELECT *

            FROM payments

            WHERE provider_payment_id = ?

            """,

            (
                provider_payment_id,
            ),
        )


        return (
            PaymentRepository._to_entity(row)
            if row
            else None
        )


    @staticmethod
    def get_by_user(
        user_id: int,
    ) -> list[Payment]:


        rows = db.fetchall(
            """
            SELECT *

            FROM payments

            WHERE user_id = ?

            ORDER BY created_at DESC

            """,

            (
                user_id,
            ),
        )


        return [
            PaymentRepository._to_entity(row)
            for row in rows
        ]


    @staticmethod
    def update_status(
        payment_id: int,
        status: str,
    ):


        db.execute(
            """
            UPDATE payments

            SET

                status = ?

            WHERE id = ?

            """,

            (
                status,

                payment_id,
            ),
        )


    @staticmethod
    def mark_paid(
        payment_id: int,
    ):


        db.execute(
            """
            UPDATE payments

            SET

                status = 'paid',

                paid_at = ?

            WHERE id = ?

            """,

            (
                int(
                    datetime.now().timestamp()
                ),

                payment_id,
            ),
        )


payment_repo = PaymentRepository()
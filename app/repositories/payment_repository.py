from datetime import datetime, timedelta

from app.database.database import db
from app.domain.payment import Payment
from app.domain.enums.payment_status import PaymentStatus



class PaymentRepository:


    @staticmethod
    def _to_entity(row):

        return Payment(

            id=row["id"],

            user_id=row["user_id"],

            subscription_id=row["subscription_id"],

            protocol=row["protocol"],

            subscription_days=row["subscription_days"],

            amount=row["amount"],

            currency=row["currency"],

            status=row["status"],

            provider=row["provider"],

            provider_payment_id=row["provider_payment_id"],

            confirmation_url=row["confirmation_url"],

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

            updated_at=(
                datetime.fromtimestamp(
                    row["updated_at"]
                )
                if "updated_at" in row.keys()
                and row["updated_at"]
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
                subscription_id,
                amount,
                currency,
                provider,
                provider_payment_id,
                confirmation_url,
                status,
                created_at,
                paid_at
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                payment.user_id,

                payment.protocol,

                payment.subscription_days,

                payment.subscription_id,

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
    def get_pending() -> list[Payment]:


        rows = db.fetchall(
            """
            SELECT *

            FROM payments

            WHERE status = 'pending'

            ORDER BY created_at ASC

            """
        )


        return [
            PaymentRepository._to_entity(row)
            for row in rows
        ]


    @staticmethod
    def get_pending_by_user_tariff(
        user_id: int,
        protocol: str,
        subscription_days: int,
        subscription_id: int | None = None,
    ) -> Payment | None:

        row = db.fetchone(
            """
            SELECT *
            FROM payments
            WHERE
                user_id = ?
                AND protocol = ?
                AND subscription_days = ?
                AND status = ?
                AND (
                    (subscription_id IS NULL AND ? IS NULL)
                    OR subscription_id = ?
                )
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                protocol,
                subscription_days,
                PaymentStatus.PENDING.value,
                subscription_id,
                subscription_id,
            ),
        )

        return (
            PaymentRepository._to_entity(row)
            if row
            else None
        )

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

        now = int(
            datetime.now().timestamp()
        )

        db.execute(
            """
            UPDATE payments

            SET

                status = 'paid',

                paid_at = ?,

                updated_at = ?

            WHERE id = ?

            """,

            (
                now,
                now,
                payment_id,
            ),
        )

    @staticmethod
    def cancel_other_pending(
        user_id: int,
        except_payment_id: int,
    ):

        db.execute(
            """
            UPDATE payments

            SET
                status = 'canceled'

            WHERE
                user_id = ?

                AND status = 'pending'

                AND id != ?
            """,
            (
                user_id,
                except_payment_id,
            ),
        )

    @staticmethod
    def mark_failed(
        payment_id: int,
    ):


        db.execute(
            """
            UPDATE payments

            SET

                status = 'failed'

            WHERE id = ?

            """,

            (
                payment_id,
            ),
        )



    @staticmethod
    def mark_canceled(
        payment_id: int,
    ):


        db.execute(
            """
            UPDATE payments

            SET

                status = 'canceled'

            WHERE id = ?

            """,

            (
                payment_id,
            ),
        )



    @staticmethod
    def expire_old_pending(
        hours: int = 24,
    ):

        limit = int(
            (
                datetime.now()
                -
                timedelta(
                    hours=hours
                )
            ).timestamp()
        )


        now = int(
            datetime.now().timestamp()
        )


        db.execute(
            """
            UPDATE payments

            SET

                status = 'expired', 

                updated_at = ?

            WHERE status = 'pending'

            AND created_at < ?

            """,

            (
                now,
                limit,
            ),
        )



    @staticmethod
    def get_all(
        limit: int = 10,
        offset: int = 0,
    ) -> list[Payment]:

        rows = db.fetchall(
            """
            SELECT *

            FROM payments

            ORDER BY created_at DESC

            LIMIT ?
            OFFSET ?

            """,

            (
                limit,
                offset,
            ),
        )


        return [
            PaymentRepository._to_entity(row)
            for row in rows
        ]



    @staticmethod
    def count() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM payments
            """
        )

        return row["total"]


    @staticmethod
    def count_paid() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM payments
            WHERE status = 'paid'
            """
        )

        return row["total"]


    @staticmethod
    def total_income() -> float:

        row = db.fetchone(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE status = 'paid'
            """
        )

        return row["total"]


    @staticmethod
    def today_income() -> float:

        from datetime import datetime

        start = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        row = db.fetchone(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE status = 'paid'
            AND paid_at >= ?
            """,
            (
                int(start.timestamp()),
            ),
        )

        return row["total"]


    @staticmethod
    def today_paid() -> int:

        from datetime import datetime

        start = datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM payments
            WHERE status = 'paid'
            AND paid_at >= ?
            """,
            (
                int(start.timestamp()),
            ),
        )

        return row["total"]

    def get_pending_by_user(
        self,
        user_id: int,
        subscription_id: int | None,
        days: int,
    ):


        row = db.fetchone(
            """
            SELECT *
            FROM payments
            WHERE user_id = ?
            AND status = ?
            AND subscription_days = ?
            AND subscription_id IS ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user_id,
                PaymentStatus.PENDING.value,
                days,
                subscription_id,
            ),
        )


        if row is None:
            return None


        return self._to_entity(
            row
        )




    
    @staticmethod
    def get_by_user_id(
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


    
payment_repo = PaymentRepository()
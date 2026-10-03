from datetime import datetime

from app.database.database import db


class WalletRepository:

    @staticmethod
    def get_balance(
        user_id: int,
    ) -> int:

        row = db.fetchone(
            """
            SELECT balance_kopecks
            FROM users
            WHERE id = ?
            """,
            (
                user_id,
            ),
        )

        if row is None:
            raise ValueError(
                "User not found"
            )

        return int(
            row["balance_kopecks"]
        )

    @staticmethod
    def credit(
        user_id: int,
        amount_kopecks: int,
        transaction_type: str = "topup",
        payment_id: int | None = None,
        description: str | None = None,
    ) -> int:

        if amount_kopecks <= 0:
            raise ValueError(
                "amount_kopecks must be greater than 0"
            )

        with db.transaction() as cursor:

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

            row = cursor.fetchone()

            if row is None:
                raise ValueError(
                    "User not found"
                )

            current_balance = int(
                row["balance_kopecks"]
            )

            new_balance = (
                current_balance
                + amount_kopecks
            )

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
                    transaction_type,
                    amount_kopecks,
                    new_balance,
                    payment_id,
                    description,
                    int(
                        datetime.now().timestamp()
                    ),
                ),
            )

            return new_balance

    @staticmethod
    def debit(
        user_id: int,
        amount_kopecks: int,
        transaction_type: str = "daily_charge",
        description: str | None = None,
    ) -> int | None:

        if amount_kopecks <= 0:
            raise ValueError(
                "amount_kopecks must be greater than 0"
            )

        with db.transaction() as cursor:

            cursor.execute(
                """
                UPDATE users
                SET balance_kopecks =
                    balance_kopecks - ?
                WHERE
                    id = ?
                    AND balance_kopecks >= ?
                """,
                (
                    amount_kopecks,
                    user_id,
                    amount_kopecks,
                ),
            )

            if cursor.rowcount != 1:

                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id = ?
                    """,
                    (
                        user_id,
                    ),
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "User not found"
                    )

                return None

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

            row = cursor.fetchone()

            new_balance = int(
                row["balance_kopecks"]
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
                    transaction_type,
                    -amount_kopecks,
                    new_balance,
                    None,
                    description,
                    int(
                        datetime.now().timestamp()
                    ),
                ),
            )

            return new_balance

    @staticmethod
    def get_transactions(
        user_id: int,
        limit: int = 50,
    ) -> list[dict]:

        rows = db.fetchall(
            """
            SELECT
                id,
                user_id,
                type,
                amount_kopecks,
                balance_after_kopecks,
                payment_id,
                description,
                created_at
            FROM wallet_transactions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        )

        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "type": row["type"],
                "amount_kopecks": row["amount_kopecks"],
                "balance_after_kopecks": row[
                    "balance_after_kopecks"
                ],
                "payment_id": row["payment_id"],
                "description": row["description"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


wallet_repo = WalletRepository()

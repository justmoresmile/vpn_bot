from app.database.database import db


class EmailAuthRepository:

    # ==============================
    # CREATE CODE
    # ==============================

    @staticmethod
    def create_code(
        email: str,
        code_hash: str,
        expires_at: int,
    ) -> int:

        email = email.strip().lower()

        # Старые неиспользованные коды этого email
        # больше не должны работать.
        db.execute(
            """
            UPDATE email_auth_codes
            SET used_at = strftime('%s','now')
            WHERE
                LOWER(email) = ?
                AND used_at IS NULL
            """,
            (
                email,
            ),
        )

        db.execute(
            """
            INSERT INTO email_auth_codes
            (
                email,
                code_hash,
                expires_at,
                attempts
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                email,
                code_hash,
                expires_at,
            ),
        )

        row = db.fetchone(
            """
            SELECT id
            FROM email_auth_codes
            WHERE LOWER(email) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                email,
            ),
        )

        if row is None:
            raise RuntimeError(
                "Failed to create email auth code"
            )

        return int(
            row["id"]
        )

    # ==============================
    # GET ACTIVE CODE
    # ==============================

    @staticmethod
    def get_active_code(
        email: str,
        now: int,
    ):

        email = email.strip().lower()

        return db.fetchone(
            """
            SELECT *
            FROM email_auth_codes
            WHERE
                LOWER(email) = ?
                AND used_at IS NULL
                AND expires_at > ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                email,
                now,
            ),
        )

    # ==============================
    # GET LATEST CODE
    # ==============================

    @staticmethod
    def get_latest_code(
        email: str,
    ):

        email = email.strip().lower()

        return db.fetchone(
            """
            SELECT *
            FROM email_auth_codes
            WHERE LOWER(email) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                email,
            ),
        )

    # ==============================
    # INCREMENT ATTEMPTS
    # ==============================

    @staticmethod
    def increment_attempts(
        code_id: int,
    ) -> None:

        db.execute(
            """
            UPDATE email_auth_codes
            SET attempts = attempts + 1
            WHERE id = ?
            """,
            (
                code_id,
            ),
        )

    # ==============================
    # MARK USED
    # ==============================

    @staticmethod
    def mark_used(
        code_id: int,
        used_at: int,
    ) -> None:

        db.execute(
            """
            UPDATE email_auth_codes
            SET used_at = ?
            WHERE id = ?
            """,
            (
                used_at,
                code_id,
            ),
        )

    # ==============================
    # INVALIDATE EMAIL CODES
    # ==============================

    @staticmethod
    def invalidate_codes(
        email: str,
        used_at: int,
    ) -> None:

        email = email.strip().lower()

        db.execute(
            """
            UPDATE email_auth_codes
            SET used_at = ?
            WHERE
                LOWER(email) = ?
                AND used_at IS NULL
            """,
            (
                used_at,
                email,
            ),
        )

    # ==============================
    # CLEANUP
    # ==============================

    @staticmethod
    def cleanup(
        older_than: int,
    ) -> None:

        db.execute(
            """
            DELETE FROM email_auth_codes
            WHERE expires_at < ?
            """,
            (
                older_than,
            ),
        )

        # ==============================
    # LAST CODE CREATED AT
    # ==============================

    @staticmethod
    def get_last_created_at(
        email: str,
    ) -> int | None:

        email = email.strip().lower()

        row = db.fetchone(
            """
            SELECT created_at
            FROM email_auth_codes
            WHERE LOWER(email) = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                email,
            ),
        )

        if row is None:
            return None

        return int(
            row["created_at"]
        )


email_auth_repo = EmailAuthRepository()
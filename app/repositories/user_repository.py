import secrets
from datetime import datetime

from app.config import settings
from app.database.database import db
from app.domain.user import User


class UsersRepository:

    @staticmethod
    def _to_entity(row):

        keys = row.keys()

        return User(
            id=row["id"],

            telegram_id=row["telegram_id"],

            email=(
                row["email"]
                if "email" in keys
                else None
            ),

            username=row["username"],

            first_name=row["first_name"],

            is_admin=bool(
                row["is_admin"]
            ),

            is_blocked=(
                bool(row["is_blocked"])
                if "is_blocked" in keys
                else False
            ),

            api_key=row["api_key"],

            vpn_provider=(
                row["vpn_provider"]
                if "vpn_provider" in keys
                else None
            ),

            provider_user_id=(
                row["provider_user_id"]
                if "provider_user_id" in keys
                else None
            ),

            provider_username=(
                row["provider_username"]
                if "provider_username" in keys
                else None
            ),
            trial_used=(
                bool(row["trial_used"])
                if "trial_used" in keys
                else False
            ),

            trial_started_at=(
                datetime.fromtimestamp(
                    row["trial_started_at"]
                )
                if (
                    "trial_started_at" in keys
                    and row["trial_started_at"]
                )
                else None
            ),

            trial_ends_at=(
                datetime.fromtimestamp(
                    row["trial_ends_at"]
                )
                if (
                    "trial_ends_at" in keys
                    and row["trial_ends_at"]
                )
                else None
            ),
        )

    # ==============================
    # GET BY TELEGRAM
    # ==============================

    @staticmethod
    def get_by_telegram(
        telegram_id: int,
    ) -> User | None:

        row = db.fetchone(
            """
            SELECT *
            FROM users
            WHERE telegram_id = ?
            """,
            (
                telegram_id,
            ),
        )

        return (
            UsersRepository._to_entity(row)
            if row
            else None
        )

    # ==============================
    # GET BY EMAIL
    # ==============================

    @staticmethod
    def get_by_email(
        email: str,
    ) -> User | None:

        email = email.strip().lower()

        row = db.fetchone(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
            """,
            (
                email,
            ),
        )

        return (
            UsersRepository._to_entity(row)
            if row
            else None
        )

    # ==============================
    # CREATE
    # ==============================

    @staticmethod
    def create(
        user: User,
    ) -> User:

        if (
            user.telegram_id is None
            and not user.email
        ):
            raise ValueError(
                "User must have telegram_id or email"
            )

        api_key = secrets.token_hex(32)

        is_admin = (
            user.telegram_id is not None
            and user.telegram_id == settings.admin_id
        )

        email = (
            user.email.strip().lower()
            if user.email
            else None
        )

        created_at = int(
            datetime.now().timestamp()
        )

        db.execute(
            """
            INSERT INTO users
            (
                telegram_id,
                email,
                username,
                first_name,
                is_admin,
                api_key,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.telegram_id,
                email,
                user.username,
                user.first_name,
                int(is_admin),
                api_key,
                created_at,
            ),
        )

        created = (
            UsersRepository.get_by_api_key(
                api_key
            )
        )

        if created is None:
            raise RuntimeError(
                "Failed to create user"
            )

        return created

    # ==============================
    # CLAIM TRIAL
    # ==============================

    @staticmethod
    def claim_trial(
        user_id: int,
        started_at: datetime,
        ends_at: datetime,
    ) -> bool:

        cursor = db.execute(
            """
            UPDATE users
            SET
                trial_used = 1,
                trial_started_at = ?,
                trial_ends_at = ?
            WHERE
                id = ?
                AND trial_used = 0
            """,
            (
                int(started_at.timestamp()),
                int(ends_at.timestamp()),
                user_id,
            ),
        )

        return cursor.rowcount == 1

    @staticmethod
    def release_trial(
        user_id: int,
        started_at: datetime,
    ) -> bool:

        cursor = db.execute(
            """
            UPDATE users
            SET
                trial_used = 0,
                trial_started_at = NULL,
                trial_ends_at = NULL
            WHERE
                id = ?
                AND trial_used = 1
                AND trial_started_at = ?
            """,
            (
                user_id,
                int(started_at.timestamp()),
            ),
        )

        return cursor.rowcount == 1

    # ==============================
    # CLAIM TRIAL FINISH
    # ==============================

    @staticmethod
    def claim_trial_finish(
        user_id: int,
        current_ends_at: datetime,
        finished_at: datetime,
    ) -> bool:

        cursor = db.execute(
            """
            UPDATE users
            SET trial_ends_at = ?
            WHERE
                id = ?
                AND trial_used = 1
                AND trial_ends_at = ?
                AND trial_ends_at > ?
            """,
            (
                int(finished_at.timestamp()),
                user_id,
                int(current_ends_at.timestamp()),
                int(finished_at.timestamp()),
            ),
        )

        return cursor.rowcount == 1

    # ==============================
    # RESTORE TRIAL FINISH
    # ==============================

    @staticmethod
    def restore_trial_finish(
        user_id: int,
        finished_at: datetime,
        original_ends_at: datetime,
    ) -> bool:

        cursor = db.execute(
            """
            UPDATE users
            SET trial_ends_at = ?
            WHERE
                id = ?
                AND trial_used = 1
                AND trial_ends_at = ?
            """,
            (
                int(original_ends_at.timestamp()),
                user_id,
                int(finished_at.timestamp()),
            ),
        )

        return cursor.rowcount == 1

    # ==============================
    # UPDATE PROFILE
    # ==============================

    @staticmethod
    def update_profile(
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ):

        db.execute(
            """
            UPDATE users
            SET
                username = ?,
                first_name = ?
            WHERE telegram_id = ?
            """,
            (
                username,
                first_name,
                telegram_id,
            ),
        )

    # ==============================
    # SET EMAIL
    # ==============================

    @staticmethod
    def set_email(
        user_id: int,
        email: str,
    ):

        email = email.strip().lower()

        db.execute(
            """
            UPDATE users
            SET email = ?
            WHERE id = ?
            """,
            (
                email,
                user_id,
            ),
        )

    # ==============================
    # GET BY ID
    # ==============================

    @staticmethod
    def get_by_id(
        user_id: int,
    ) -> User | None:

        row = db.fetchone(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (
                user_id,
            ),
        )

        return (
            UsersRepository._to_entity(row)
            if row
            else None
        )

    # ==============================
    # GET BY API KEY
    # ==============================

    @staticmethod
    def get_by_api_key(
        api_key: str,
    ) -> User | None:

        row = db.fetchone(
            """
            SELECT *
            FROM users
            WHERE api_key = ?
            """,
            (
                api_key,
            ),
        )

        return (
            UsersRepository._to_entity(row)
            if row
            else None
        )

    # ==============================
    # GET ALL
    # ==============================

    @staticmethod
    def get_all() -> list[User]:

        rows = db.fetchall(
            """
            SELECT *
            FROM users
            ORDER BY id DESC
            """
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    # ==============================
    # COUNT
    # ==============================

    @staticmethod
    def count() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM users
            """
        )

        return row["total"]

    # ==============================
    # SEARCH
    # ==============================

    @staticmethod
    def search(
        query: str,
    ):

        value = f"%{query}%"

        rows = db.fetchall(
            """
            SELECT *
            FROM users
            WHERE
                username LIKE ?
                OR first_name LIKE ?
                OR email LIKE ?
                OR CAST(
                    telegram_id AS TEXT
                ) LIKE ?
            ORDER BY id DESC
            """,
            (
                value,
                value,
                value,
                value,
            ),
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    # ==============================
    # ADMIN FILTERS
    # ==============================

    @staticmethod
    def get_admins() -> list[User]:

        rows = db.fetchall(
            """
            SELECT *
            FROM users
            WHERE is_admin = 1
            ORDER BY id DESC
            """
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    @staticmethod
    def get_without_subscription() -> list[User]:

        rows = db.fetchall(
            """
            SELECT *
            FROM users u

            WHERE NOT EXISTS
            (
                SELECT 1
                FROM subscriptions s
                WHERE s.user_id = u.id
            )

            ORDER BY u.id DESC
            """
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    @staticmethod
    def get_active_subscription_users() -> list[User]:

        rows = db.fetchall(
            """
            SELECT DISTINCT u.*

            FROM users u

            JOIN subscriptions s
            ON s.user_id = u.id

            WHERE s.status = 'active'

            ORDER BY u.id DESC
            """
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    @staticmethod
    def get_expired_subscription_users() -> list[User]:

        rows = db.fetchall(
            """
            SELECT DISTINCT u.*

            FROM users u

            JOIN subscriptions s
            ON s.user_id = u.id

            WHERE s.status = 'expired'

            ORDER BY u.id DESC
            """
        )

        return [
            UsersRepository._to_entity(row)
            for row in rows
        ]

    # ==============================
    # BLOCK
    # ==============================

    @staticmethod
    def block(
        user_id: int,
    ):

        db.execute(
            """
            UPDATE users
            SET is_blocked = 1
            WHERE id = ?
            """,
            (
                user_id,
            ),
        )

    # ==============================
    # UNBLOCK
    # ==============================

    @staticmethod
    def unblock(
        user_id: int,
    ):

        db.execute(
            """
            UPDATE users
            SET is_blocked = 0
            WHERE id = ?
            """,
            (
                user_id,
            ),
        )

    # ==============================
    # COUNT BLOCKED
    # ==============================

    @staticmethod
    def count_blocked() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE is_blocked = 1
            """
        )

        return row["total"]

    # ==============================
    # COUNT ADMINS
    # ==============================

    @staticmethod
    def count_admins() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE is_admin = 1
            """
        )

        return row["total"]

    # ==============================
    # GET BLOCKED
    # ==============================

    @staticmethod
    def get_blocked():

        rows = db.fetchall(
            """
            SELECT *
            FROM users
            WHERE is_blocked = 1
            ORDER BY id DESC
            """
        )

        return rows

    # ==============================
    # VPN PROVIDER
    # ==============================

    @staticmethod
    def set_vpn_provider(
        user_id: int,
        provider: str | None,
        provider_user_id: int | None,
        provider_username: str | None,
    ) -> None:

        db.execute(
            """
            UPDATE users
            SET
                vpn_provider = ?,
                provider_user_id = ?,
                provider_username = ?
            WHERE id = ?
            """,
            (
                provider,
                provider_user_id,
                provider_username,
                user_id,
            ),
        )


users_repo = UsersRepository()

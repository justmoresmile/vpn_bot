from app.database.database import db
from app.domain.user import User
from app.config import settings
from datetime import datetime

class UsersRepository:

    @staticmethod
    def _to_entity(row):

        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            is_admin=bool(row["is_admin"]),
            api_key=row["api_key"],
            created_at=(
                datetime.fromtimestamp(row["created_at"])
                if "created_at" in row.keys()
                and row["created_at"]
                else None
            ),
        )


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


    @staticmethod
    def create(
         user: User,
     ) -> User:
 
         import secrets
 
         api_key = secrets.token_hex(32)
 
         is_admin = (
             user.telegram_id == settings.admin_id
         )
         created_at = int(
            datetime.now().timestamp()
        )
 
         db.execute(
             """
             INSERT INTO users
             (
                 telegram_id,
                 username,
                 first_name,
                 is_admin,
                 api_key,
                 created_at
             )
             VALUES (?, ?, ?, ?, ?)
             """,
             (
                 user.telegram_id,
                 user.username,
                 user.first_name,
                 int(is_admin),
                 api_key,
                 created_at,
             ),
         )
 
         return UsersRepository.get_by_telegram(
             user.telegram_id
         )
 

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


    @staticmethod
    def count() -> int:

        row = db.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM users
            """
        )

        return row["total"]


    @staticmethod
    def search(query: str):

        rows = db.fetchall(
            """
            SELECT
                id,
                telegram_id,
                username,
                first_name,
                is_admin,
                api_key,
                created_at
            FROM users
            WHERE
                username LIKE ?
                OR first_name LIKE ?
                OR telegram_id LIKE ?
            """,
            (
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
            )
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

            WHERE NOT EXISTS (

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

users_repo = UsersRepository()
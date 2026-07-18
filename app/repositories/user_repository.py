from app.database.database import db
from app.domain.user import User


class UsersRepository:

    @staticmethod
    def _to_entity(row) -> User:
        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            is_admin=bool(row["is_admin"]),
        )

    @staticmethod
    def get_by_telegram(telegram_id: int) -> User | None:
        row = db.fetchone(
            """
            SELECT *
            FROM users
            WHERE telegram_id = ?
            """,
            (telegram_id,),
        )

        return UsersRepository._to_entity(row) if row else None

    @staticmethod
    def create(user: User) -> User:
        db.execute(
            """
            INSERT INTO users
            (
                telegram_id,
                username,
                first_name,
                is_admin
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user.telegram_id,
                user.username,
                user.first_name,
                int(user.is_admin),
            ),
        )

        return UsersRepository.get_by_telegram(user.telegram_id)
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

users_repo = UsersRepository()
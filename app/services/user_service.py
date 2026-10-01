from app.domain.user import User

from app.repositories.user_repository import (
    users_repo,
)


class UserService:

    # ==============================
    # TELEGRAM
    # ==============================

    def sync_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ):

        user = self.get_by_telegram(
            telegram_id
        )

        if user is None:

            user = User(
                id=None,
                telegram_id=telegram_id,
                email=None,
                username=username,
                first_name=first_name,
                is_admin=False,
            )

            user = users_repo.create(
                user
            )

            return True, user

        users_repo.update_profile(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )

        return (
            False,
            self.get_by_telegram(
                telegram_id
            ),
        )

    # ==============================
    # EMAIL
    # ==============================

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return users_repo.get_by_email(
            email
        )

    def create_by_email(
        self,
        email: str,
    ) -> User:

        email = email.strip().lower()

        user = self.get_by_email(
            email
        )

        if user is not None:
            return user

        user = User(
            id=None,
            telegram_id=None,
            email=email,
            username=None,
            first_name=None,
            is_admin=False,
        )

        return users_repo.create(
            user
        )

    def attach_email(
        self,
        user_id: int,
        email: str,
    ) -> User:

        email = email.strip().lower()

        existing = self.get_by_email(
            email
        )

        if (
            existing is not None
            and existing.id != user_id
        ):
            raise ValueError(
                "Email already belongs to another user"
            )

        users_repo.set_email(
            user_id=user_id,
            email=email,
        )

        user = users_repo.get_by_id(
            user_id
        )

        if user is None:
            raise ValueError(
                "User not found"
            )

        return user

    # ==============================
    # GETTERS
    # ==============================

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        return users_repo.get_by_id(
            user_id
        )

    def get_by_telegram(
        self,
        telegram_id: int,
    ) -> User | None:

        return users_repo.get_by_telegram(
            telegram_id
        )

    def get_all(
        self,
    ) -> list[User]:

        return users_repo.get_all()

    # ==============================
    # ADMIN
    # ==============================

    def is_admin(
        self,
        telegram_id: int,
    ) -> bool:

        user = self.get_by_telegram(
            telegram_id
        )

        if user is None:
            return False

        return user.is_admin


user_service = UserService()
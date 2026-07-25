from app.domain.user import User

from app.repositories.user_repository import (
    users_repo,
)


class UserService:


    def sync_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str |None,
    ):

        user = self.get_by_telegram(
            telegram_id
        )

        if user is None:

            user = User(
                id=None,
                telegram_id=telegram_id,
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
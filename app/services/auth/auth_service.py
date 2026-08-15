from app.repositories.user_repository import users_repo
from app.services.auth.jwt_service import jwt_service
from app.config import settings
from app.services.user_service import (
    user_service,
)

class AuthService:


    def login_by_api_key(
        self,
        api_key: str,
    ) -> str | None:

        user = users_repo.get_by_api_key(
            api_key
        )

        if user is None:
            return None

        return jwt_service.create_token(
            user.id
        )


    def login_by_telegram(
        self,
        telegram_id: int,
    ) -> str | None:

        user = users_repo.get_by_telegram(
            telegram_id
        )

        if user is None:
            return None

        return jwt_service.create_token(
            user.id
        )



    def get_current_user(
        self,
        token: str,
    ):

        user_id = jwt_service.get_user_id(
            token
        )

        if user_id is None:
            return None

        return users_repo.get_by_id(
            user_id
        )


    def login_by_telegram_webapp(
        self,
        init_data: str,
    ) -> str | None:

        telegram_user = (
            telegram_webapp_auth.validate_init_data(
                init_data
            )
        )

        if telegram_user is None:
            return None

        _, user = user_service.sync_user(
            telegram_id=telegram_user["telegram_id"],
            username=telegram_user["username"],
            first_name=telegram_user["first_name"],
        )

        if user is None:
            return None

        return jwt_service.create_token(
            user.id
        )

auth_service = AuthService()
from app.repositories.user_repository import users_repo
from app.services.auth.jwt_service import jwt_service
from app.config import settings


class AuthService:


    def login_by_api_key(
        self,
        telegram_id: int,
        api_key: str,
    ) -> str | None:

        user = users_repo.get_by_telegram(
            telegram_id
        )

        if user is None:
            return None

        if user.api_key != api_key:
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


auth_service = AuthService()
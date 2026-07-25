from datetime import datetime, timedelta, UTC

import jwt

from app.config import settings


class JWTService:


    def create_token(
        self,
        user_id: int,
    ) -> str:

        now = datetime.now(UTC)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": (
                now
                +
                timedelta(
                    days=settings.jwt_expire_days
                )
            ),
        }


        return jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )



    def verify_token(
        self,
        token: str,
    ) -> dict | None:

        try:

            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[
                    settings.jwt_algorithm
                ],
            )

            return payload


        except jwt.ExpiredSignatureError:

            return None


        except jwt.InvalidTokenError:

            return None



    def get_user_id(
        self,
        token: str,
    ) -> int | None:

        payload = self.verify_token(
            token
        )


        if payload is None:
            return None


        if payload.get("type") != "access":
            return None


        try:

            return int(
                payload["sub"]
            )


        except (
            KeyError,
            ValueError,
            TypeError,
        ):

            return None



jwt_service = JWTService()
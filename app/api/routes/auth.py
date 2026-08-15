from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from app.services.auth.auth_service import auth_service
from app.services.auth.jwt_service import jwt_service
from app.services.auth.telegram_webapp_auth import (
    telegram_webapp_auth,
)
from app.services.user_service import user_service

from app.api.dependencies.internal import (
    verify_internal_api_key,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class TokenRequest(BaseModel):
    api_key: str


class InternalTokenRequest(BaseModel):
    telegram_id: int


class TelegramWebAppRequest(BaseModel):
    init_data: str


@router.post(
    "/token"
)
async def create_token(
    request: TokenRequest,
):
    token = auth_service.login_by_api_key(
        api_key=request.api_key,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post(
    "/internal/token",
)
async def create_internal_token(
    request: InternalTokenRequest,
    _: bool = Depends(
        verify_internal_api_key
    ),
):
    token = auth_service.login_by_telegram(
        telegram_id=request.telegram_id,
    )

    if token is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post(
    "/telegram",
)
async def create_telegram_token(
    request: TelegramWebAppRequest,
):
    user_data = (
        telegram_webapp_auth.validate_init_data(
            request.init_data
        )
    )

    if user_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram init data",
        )

    _, user = user_service.sync_user(
        telegram_id=user_data["telegram_id"],
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
    )

    token = jwt_service.create_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
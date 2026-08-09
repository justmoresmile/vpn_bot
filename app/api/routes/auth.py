from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from app.services.auth.auth_service import auth_service
from app.api.dependencies.internal import verify_internal_api_key


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class TokenRequest(BaseModel):
    api_key: str


class InternalTokenRequest(BaseModel):
    telegram_id: int


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
    _: bool = Depends(verify_internal_api_key),
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
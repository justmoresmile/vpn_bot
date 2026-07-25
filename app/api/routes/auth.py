from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

from app.services.auth.auth_service import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class TokenRequest(BaseModel):

    telegram_id: int
    api_key: str



@router.post(
    "/token"
)
async def create_token(
    request: TokenRequest,
):

    token = auth_service.login_by_api_key(
        telegram_id=request.telegram_id,
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
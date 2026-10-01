from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from app.api.dependencies.internal import (
    verify_internal_api_key,
)
from app.api.schemas.auth import (
    EmailCodeRequest,
    EmailCodeRequestResponse,
    EmailCodeVerifyRequest,
    EmailCodeVerifyResponse,
)
from app.services.auth.auth_service import auth_service
from app.services.auth.email_auth_service import (
    email_auth_service,
)
from app.services.auth.jwt_service import jwt_service
from app.services.auth.telegram_webapp_auth import (
    telegram_webapp_auth,
)
from app.services.user_service import user_service
from loguru import logger


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


# ============================================================
# API KEY AUTH
# ============================================================

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


# ============================================================
# INTERNAL TELEGRAM AUTH
# ============================================================

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


# ============================================================
# TELEGRAM WEB APP AUTH
# ============================================================

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


# ============================================================
# EMAIL AUTH - REQUEST CODE
# ============================================================

@router.post(
    "/email/request-code",
    response_model=EmailCodeRequestResponse,
)
async def request_email_code(
    request: EmailCodeRequest,
):

    try:
        expires_in = (
            await email_auth_service.create_login_code(
                request.email
            )
        )

    except RuntimeError as exc:

        error = str(exc)

        if error.startswith("RATE_LIMIT:"):

            retry_after = int(
                error.split(
                    ":",
                    1,
                )[1]
            )

            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Too many code requests",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(
                        retry_after
                    )
                },
            )

        logger.exception(
            "Failed to send email login code"
        )

        raise HTTPException(
            status_code=503,
            detail="Failed to send email code",
        )

    except Exception as exc:

        logger.exception(
            "Failed to send email login code"
        )

        raise HTTPException(
            status_code=503,
            detail="Failed to send email code",
        )

    return EmailCodeRequestResponse(
        success=True,
        expires_in=expires_in,
    )


# ============================================================
# EMAIL AUTH - VERIFY CODE
# ============================================================

@router.post(
    "/email/verify-code",
    response_model=EmailCodeVerifyResponse,
)
async def verify_email_code(
    request: EmailCodeVerifyRequest,
):

    token = (
        email_auth_service.verify_login_code(
            email=request.email,
            code=request.code,
        )
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired code",
        )

    return EmailCodeVerifyResponse(
        access_token=token,
        token_type="bearer",
    )
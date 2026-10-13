from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from app.api.dependencies.internal import (
    verify_internal_api_key,
)
from app.api.dependencies.auth import (
    get_current_user,
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


class TelegramEmailLinkRequest(BaseModel):
    email: str
    code: str
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
# LINK EXISTING EMAIL ACCOUNT WITH TELEGRAM
# ============================================================

@router.post(
    "/email/link-telegram",
)
async def link_email_account_to_telegram(
    request: TelegramEmailLinkRequest,
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

    verified_email = (
        email_auth_service.verify_code_only(
            email=request.email,
            code=request.code,
        )
    )

    if verified_email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired code",
        )

    existing_email_user = (
        user_service.get_by_email(
            verified_email
        )
    )

    if existing_email_user is None:
        raise HTTPException(
            status_code=404,
            detail="Email account not found",
        )

    try:

        user = user_service.attach_telegram(
            user_id=existing_email_user.id,
            telegram_id=user_data["telegram_id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    token = jwt_service.create_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }



# ============================================================
# ATTACH EMAIL TO CURRENT USER
# ============================================================

@router.post(
    "/email/attach",
)
async def attach_email_to_current_user(
    request: EmailCodeVerifyRequest,
    current_user = Depends(
        get_current_user
    ),
):

    verified_email = (
        email_auth_service.verify_code_only(
            email=request.email,
            code=request.code,
        )
    )

    if verified_email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired code",
        )

    try:

        user = user_service.attach_email(
            user_id=current_user.id,
            email=verified_email,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return {
        "success": True,
        "user_id": user.id,
        "email": user.email,
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
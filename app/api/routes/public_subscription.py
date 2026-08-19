from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)

from fastapi.responses import PlainTextResponse

from app.logger import logger

from app.repositories.subscription_repository import (
    subscription_repo,
)

from app.services.device_service import (
    device_service,
)

from app.services.vpn_service import (
    vpn_service,
)


router = APIRouter()


async def serve_subscription(
    token: str,
    request: Request,
    device_token: str | None = None,
):

    subscription = (
        subscription_repo.get_by_token(
            token
        )
    )

    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    if subscription.status.value != "active":

        raise HTTPException(
            status_code=403,
            detail="Subscription is not active",
        )

    device_info = (
        device_service.detect(
            request
        )
    )

    if device_info is not None:

        device_service.register(
            subscription=subscription,
            device_info=device_info,
            device_token=device_token,
        )

    else:

        logger.info(
            "Subscription client without device identifier: "
            "subscription_id={} "
            "user_agent={}",
            subscription.id,
            request.headers.get(
                "user-agent"
            ),
        )

    config = await vpn_service.get_config(
        subscription.id
    )

    if not config:

        raise HTTPException(
            status_code=404,
            detail="Subscription config not found",
        )

    return config


# ============================================================
# DEVICE-SPECIFIC SUBSCRIPTION
# ============================================================

@router.get(
    "/{token}/{device_token}",
    response_class=PlainTextResponse,
)
async def get_device_subscription(
    token: str,
    device_token: str,
    request: Request,
):

    return await serve_subscription(
        token=token,
        request=request,
        device_token=device_token,
    )


# ============================================================
# LEGACY / FIRST DEVICE SUBSCRIPTION
# ============================================================

@router.get(
    "/{token}",
    response_class=PlainTextResponse,
)
async def get_public_subscription(
    token: str,
    request: Request,
):

    return await serve_subscription(
        token=token,
        request=request,
    )
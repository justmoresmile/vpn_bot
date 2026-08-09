
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.repositories.subscription_repository import subscription_repo
from app.services.vpn_service import vpn_service


router = APIRouter()


@router.get(
    "/{token}",
    response_class=PlainTextResponse,
)
async def get_public_subscription(
    token: str,
):
    subscription = subscription_repo.get_by_token(
        token
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

    config = await vpn_service.get_config(
        subscription.id
    )

    if not config:
        raise HTTPException(
            status_code=404,
            detail="Subscription config not found",
        )

    return config


from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
import qrcode
from io import BytesIO
from fastapi.responses import Response

from app.api.schemas.subscription import (
    ConfigResponse,
    RenewResponse,
    SubscriptionResponse,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User

from app.services.subscription_service import (
    subscription_service,
)

from app.services.vpn_service import (
    vpn_service,
)


router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"],
)



def check_subscription_owner(
    subscription,
    user: User,
):
    if subscription.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )



@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse,
)
async def get_subscription(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    check_subscription_owner(
        subscription,
        user,
    )


    return SubscriptionResponse(

        id=subscription.id,

        user_id=subscription.user_id,

        protocol=subscription.protocol,

        status=subscription.status.value,

        expires_at=subscription.expires_at,

        config=subscription.config,

        client_email=subscription.client_email,

    )



@router.get(
    "/{subscription_id}/config",
    response_model=ConfigResponse,
)
async def get_config(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    check_subscription_owner(
        subscription,
        user,
    )


    config = await vpn_service.get_config(
        subscription_id
    )


    if config is None:

        raise HTTPException(
            status_code=404,
            detail="Config not found",
        )


    return ConfigResponse(
        config=config,
    )



@router.post(
    "/{subscription_id}/renew",
    response_model=RenewResponse,
)
async def renew_subscription(
    subscription_id: int,
    days: int = 30,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    check_subscription_owner(
        subscription,
        user,
    )


    subscription = await vpn_service.renew(
        subscription_id,
        days,
    )


    return RenewResponse(

        id=subscription.id,

        status=subscription.status.value,

        expires_at=subscription.expires_at,

    )

@router.get(
    "/{subscription_id}/qr"
)
async def get_qr(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    config = await vpn_service.get_config(
        subscription_id
    )

    if not config:

        raise HTTPException(
            status_code=404,
            detail="Config not found",
        )

    image = qrcode.make(config)

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
    )


@router.get(
    "/{subscription_id}/file"
)
async def download_file(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    subscription = subscription_service.get_by_id(
        subscription_id
    )

    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    check_subscription_owner(
        subscription,
        user,
    )

    filename, content = await vpn_service.get_file(
        subscription
    )

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )
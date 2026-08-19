from fastapi import (
    APIRouter,
    Depends,
)

from app.api.schemas.user import (
    UserResponse,
    SyncUserRequest,
    SyncUserResponse,
)

from app.api.schemas.subscription import (
    SubscriptionShortResponse,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User

from app.services.subscription_service import (
    subscription_service,
)

from app.services.user_service import (
    user_service,
)

from app.services.payment_service import payment_service
from app.api.schemas.payment import PaymentResponse
from app.services.server_service import server_service

router = APIRouter(
    prefix="/user",
    tags=["User"],
)



@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    user: User = Depends(
        get_current_user
    ),
):

    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        is_admin=user.is_admin,
    )


@router.get(
    "/me/subscriptions",
    response_model=list[SubscriptionShortResponse],
)
async def my_subscriptions(
    user: User = Depends(
        get_current_user
    ),
):

    subscriptions = subscription_service.get_by_user(
        user.id
    )

    result = []

    for s in subscriptions:

        try:
            server = server_service.get_by_id(
                s.server_id
            )
        except RuntimeError:
            server = None

        result.append(
            SubscriptionShortResponse(
                id=s.id,
                protocol=s.protocol,
                status=s.status.value,
                expires_at=s.expires_at,
                client_email=s.client_email,
                server_name=(
                    server.name
                    if server
                    else None
                ),
                server_country=(
                    server.country
                    if server
                    else None
                ),
            )
        )

    return result


@router.post(
    "/sync",
    response_model=SyncUserResponse,
)
async def sync_user(
    request: SyncUserRequest,
):

    created, user = user_service.sync_user(
        telegram_id=request.telegram_id,
        username=request.username,
        first_name=request.first_name,
    )

    return SyncUserResponse(
        created=created,
        id=user.id,
    )

@router.get(
"/me/payments",
    response_model=list[PaymentResponse],
)
async def get_my_payments(
    current_user = Depends(
        get_current_user
    ),
):

    payments = (
        payment_service
        .get_user_payments(
            current_user.id
        )
    )


    return [
        PaymentResponse(

            id=payment.id,

            amount=payment.amount,

            currency=payment.currency,

            protocol=payment.protocol,

            subscription_days=(
                payment.subscription_days
            ),

            status=payment.status,

            created_at=payment.created_at,

            paid_at=payment.paid_at,

        )

        for payment in payments
    ]


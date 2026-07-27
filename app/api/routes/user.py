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

    return [
    SubscriptionShortResponse(
        id=s.id,
        protocol=s.protocol,
        status=s.status.value,
        expires_at=s.expires_at,
        client_email=s.client_email,
        )
        for s in subscriptions
    ]



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




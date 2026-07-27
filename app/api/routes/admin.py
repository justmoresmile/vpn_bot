
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import Response

from app.api.dependencies.auth import (
    get_current_user,
    get_current_admin,
)
from app.domain.user import User
from app.services.admin_service import admin_service
from app.repositories.subscription_repository import subscription_repo
from app.api.schemas.admin import AdminUserCardResponse
from pydantic import BaseModel

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class BroadcastRequest(BaseModel):

    target: str

    message: str


@router.get(
    "/statistics",
)
async def get_statistics(
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return admin_service.get_statistics()

@router.get(
    "/users",
)
async def get_users(
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    users = admin_service.get_users()

    return [
        {
            "id": x.id,
            "telegram_id": x.telegram_id,
            "username": x.username,
            "first_name": x.first_name,
            "is_admin": x.is_admin,
        }
        for x in users
    ]



@router.get("/payments")
async def admin_payments(
    page: int = 1,
    admin = Depends(get_current_user),
):

    payments = await admin_service.get_payments_page(
        page
    )

    return payments



@router.get(
    "/users/page",
)
async def get_users_page(
    page: int = 1,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    data = admin_service.get_users_page(
        page
    )


    return {

        "page": data["page"],

        "pages": data["pages"],

        "users": [
            {
                "id": x.id,
                "telegram_id": x.telegram_id,
                "username": x.username,
                "first_name": x.first_name,
            }
            for x in data["users"]
        ],

    }



@router.get(
    "/users/{user_id}",
)
async def get_user(
    user_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    target = admin_service.get_user(
        user_id
    )


    if target is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return {
        "id": target.id,
        "telegram_id": target.telegram_id,
        "username": target.username,
        "first_name": target.first_name,
        "is_admin": target.is_admin,
    }

@router.get(
    "/users/{user_id}/subscriptions",
)
async def get_user_subscriptions(
    user_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    subscriptions = (
        admin_service.get_user_subscriptions(
            user_id
        )
    )


    return [
        {
            "id": x.id,
            "protocol": x.protocol,
            "status": x.status.value,
            "expires_at": x.expires_at,
        }
        for x in subscriptions
    ]



@router.get(
    "/users/{user_id}/card",
    response_model=AdminUserCardResponse,
)
async def get_user_card(
    user_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    card = admin_service.get_user_card(
        user_id
    )


    if card is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return card


@router.post(
    "/subscriptions/{subscription_id}/renew",
)
async def renew_subscription(
    subscription_id: int,
    days: int = 30,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    subscription = await admin_service.renew_subscription(
        subscription_id,
        days,
    )


    return {
        "id": subscription.id,
        "status": subscription.status.value,
        "expires_at": subscription.expires_at,
    }



@router.post(
    "/subscriptions/{subscription_id}/disable",
)
async def disable_subscription(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    subscription = await admin_service.disable_subscription(
        subscription_id
    )


    return {
        "id": subscription.id,
        "status": subscription.status.value,
    }



@router.delete(
    "/subscriptions/{subscription_id}",
)
async def delete_subscription(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    await admin_service.delete_subscription(
        subscription_id
    )


    return {
        "success": True,
    }



@router.post(
    "/subscriptions/{subscription_id}/restore",
)
async def restore_subscription(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    subscription = await admin_service.restore_subscription(
        subscription_id
    )


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    return {
        "id": subscription.id,
        "status": subscription.status.value,
    }



@router.get(
    "/subscriptions/{subscription_id}/config",
)
async def get_subscription_config(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    config = await admin_service.get_subscription_config(
        subscription_id
    )


    if config is None:

        raise HTTPException(
            status_code=404,
            detail="Config not found",
        )


    return {
        "config": config,
    }



@router.get(
    "/subscriptions/{subscription_id}/file",
)
async def get_subscription_file(
    subscription_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    result = await admin_service.get_subscription_file(
        subscription_id
    )


    if result is None:

        raise HTTPException(
            status_code=404,
            detail="File not found",
        )


    filename, content = result


    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )


@router.get(
    "/users/{user_id}/payments",
)
async def get_user_payments(
    user_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    payments = (
        admin_service.get_user_payments(
            user_id
        )
    )


    return [
        {
            "id": x.id,

            "amount": x.amount,

            "currency": x.currency,

            "status": x.status.value,

            "provider": x.provider,

            "protocol": x.protocol,

            "subscription_days": x.subscription_days,

            "created_at": x.created_at,

            "paid_at": x.paid_at,

        }

        for x in payments
    ]

@router.post(
    "/broadcast",
)
async def broadcast(
    data: BroadcastRequest,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    result = await admin_service.broadcast(
        data.target,
        data.message,
    )


    return result



@router.get("/subscriptions")
async def admin_subscriptions(
    page: int = 1,
    admin: User = Depends(get_current_user),
):

    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return await admin_service.get_subscriptions_page(page)




@router.get(
"/users/search",
)
async def search_users(
    q: str,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    users = admin_service.search_users(
        q
    )


    return [
        {
            "id": x.id,
            "telegram_id": x.telegram_id,
            "username": x.username,
            "first_name": x.first_name,
            "is_admin": x.is_admin,
        }
        for x in users
    ]

@router.get(
    "/users/filter",
)
async def filter_users(
    filter_type: str,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    users = admin_service.filter_users(
        filter_type
    )


    return [
        {
            "id": x.id,
            "telegram_id": x.telegram_id,
            "username": x.username,
            "first_name": x.first_name,
            "is_admin": x.is_admin,
        }
        for x in users
    ]



async def admin_subscriptions(
    admin = Depends(get_current_admin),
):

    subscriptions = subscription_repo.get_all()


    return [
        {
            "id": sub.id,
            "user_id": sub.user_id,
            "client_email": sub.client_email,
            "protocol": sub.protocol,
            "status": sub.status.value,
            "expires_at": sub.expires_at.strftime(
                "%d.%m.%Y %H:%M"
            ),
        }
        for sub in subscriptions
    ]
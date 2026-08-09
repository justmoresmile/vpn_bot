
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import Response

from app.api.dependencies.auth import (
    get_current_user,
)
from app.domain.user import User
from app.services.admin_service import admin_service
from app.repositories.subscription_repository import subscription_repo
from app.repositories.server_repository import server_repo
from app.api.schemas.admin import AdminUserCardResponse
from pydantic import BaseModel
from app.domain.server import Server
from app.services.server_service import server_service


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)
class ServerCreateRequest(BaseModel):

    name: str

    country: str

    host: str

    api_url: str

    api_token: str

    wireguard_inbound_id: int

    priority: int = 100

    enabled: bool = True



class ServerUpdateRequest(BaseModel):

    name: str

    country: str

    host: str

    api_url: str

    api_token: str

    wireguard_inbound_id: int

    priority: int

    enabled: bool




from fastapi import (
    APIRouter,
    HTTPException,
)

from app.services.admin_service import admin_service
from app.services.auth.jwt_service import jwt_service
from app.repositories.user_repository import users_repo


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
    "/dashboard",
)
async def get_dashboard(
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    return admin_service.get_dashboard()





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


    users = []


    for x in data["users"]:


        if hasattr(x, "id"):

            user_id = x.id
            telegram_id = x.telegram_id
            username = x.username
            first_name = x.first_name


        else:

            user_id = x["id"]
            telegram_id = x["telegram_id"]
            username = x.get("username")
            first_name = x.get("first_name")



        subscriptions = (
            admin_service
            .get_user_subscriptions(
                user_id
            )
        )



        payments = (
            admin_service
            .get_user_payments(
                user_id
            )
        )

        print(
            "USER:",
            user_id,
            "COUNT:",
            len(payments)
        )



        subscription_status = "none"



        if subscriptions:


            statuses = [
                s.status.value
                for s in subscriptions
            ]


            if "active" in statuses:

                subscription_status = "active"


            elif "disabled" in statuses:

                subscription_status = "disabled"


            elif "expired" in statuses:

                subscription_status = "expired"




        subscriptions_count = len(
            subscriptions
        )



        total_paid = sum(

            p.amount

            for p in payments

            if p.status == "paid"

        )




        target_user = (
    admin_service
    .get_user(
        user_id
    )
)


        users.append(
            {
                "id": user_id,

                "telegram_id": telegram_id,

                "username": username,

                "first_name": first_name,

                "is_admin": (
                    target_user.is_admin
                    if target_user
                    else False
                ),

                "is_blocked": (
                    target_user.is_blocked
                    if target_user
                    else False
                ),

                "subscription_status": subscription_status,

                "subscriptions_count": subscriptions_count,

                "total_paid": total_paid,

            }
        )



    return {

        "page": data["page"],

        "pages": data["pages"],

        "total": data["total"],

        "users": users,

    }

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


    return admin_service.build_users_response(
    users
)

@router.get(
    "/users/filter",
)
async def filter_users(
    type: str,
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
        type
    )


    return admin_service.build_users_response(
        users
    )



@router.get(
"/users/statistics",
)
async def get_users_statistics(
        user: User = Depends(
            get_current_user
        ),
    ):

        if not user.is_admin:

            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )


        return admin_service.get_users_statistics()






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
        "is_blocked": target.is_blocked,
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
    days: int,
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


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
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


    subscription = subscription_repo.get_by_id(
    subscription_id
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    filename = (
        f"{subscription.client_email}.conf"
    )


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
    limit: int = 10,
    admin: User = Depends(get_current_user),
):

    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return await admin_service.get_subscriptions_page(
        page=page,
        limit=limit,
    )

@router.get(
    "/subscriptions/{subscription_id}"
)
async def get_admin_subscription(
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


    subscription = (
        admin_service
        .get_subscription(
            subscription_id
        )
    )


    if subscription is None:

        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )


    return subscription


@router.post(
    "/users/{user_id}/subscription"
)
async def create_user_subscription(
    user_id: int,
    days: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    subscription = await admin_service.create_subscription(
        user_id=user_id,
        days=days,
    )


    return {
        "id": subscription.id,
        "status": subscription.status.value,
        "expires_at": subscription.expires_at,
    }


@router.post("/login")
async def admin_login(
    data: dict,
):

    api_key = data.get(
        "api_key"
    )


    if not api_key:

        raise HTTPException(
            status_code=400,
            detail="API key required",
        )


    user = (
        users_repo
        .get_by_api_key(
            api_key
        )
    )


    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )


    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )


    token = jwt_service.create_token(
        user.id
    )


    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get(
    "/servers",
)
async def get_admin_servers(
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    servers = server_repo.get_all()


    return [

        {
            "id": server.id,

            "name": server.name,

            "country": server.country,

            "host": server.host,

            "enabled": server.enabled,

            "priority": server.priority,

            "wireguard_inbound_id":
                server.wireguard_inbound_id,

        }

        for server in servers

    ]




@router.post(
    "/servers"
)
async def create_admin_server(
    data: ServerCreateRequest,
    user: User = Depends(
        get_current_user
    ),
):


    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    server = server_repo.create(

    Server(

        id=None,

        name=data.name,

        country=data.country,

        host=data.host,

        api_url=data.api_url,

        api_token=data.api_token,

        wireguard_inbound_id=data.wireguard_inbound_id,

        enabled=data.enabled,

        priority=data.priority,

    )

)


    return {

        "id": server.id,

        "name": server.name,

        "country": server.country,

        "host": server.host,

        "enabled": server.enabled,

        "priority": server.priority,

        "wireguard_inbound_id":
            server.wireguard_inbound_id,

    }







@router.get(
    "/servers/{server_id}"
)
async def get_admin_server(
    server_id: int,
    user: User = Depends(
        get_current_user
    ),
):


    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    server = (
        server_repo
        .get_by_id(
            server_id
        )
    )


    if server is None:

        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )



    return {
        "api_url": server.api_url,  
        "api_token": server.api_token,
        "id": server.id,

        "name": server.name,

        "country": server.country,

        "host": server.host,

        "enabled": server.enabled,

        "priority": server.priority,

        "wireguard_inbound_id":
            server.wireguard_inbound_id,

    }


@router.post(
    "/servers/{server_id}/check"
)
async def check_admin_server(
    server_id: int,
    user: User = Depends(
        get_current_user
    ),
):


    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )



    result = await admin_service.check_server(
        server_id
    )



    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )



    return result



@router.get(
    "/servers/{server_id}/stats"
)
async def get_server_stats(
    server_id: int,
    user: User = Depends(
        get_current_user
    ),
):


    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    stats = await admin_service.get_server_stats(
        server_id
    )


    if stats is None:

        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )


    return stats





@router.put(
    "/servers/{server_id}"
)
async def update_admin_server(
    server_id: int,
    data: ServerUpdateRequest,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    server = server_repo.get_by_id(
        server_id
    )


    if server is None:

        raise HTTPException(
            status_code=404,
            detail="Server not found",
        )


    server.name = data.name
    server.country = data.country
    server.host = data.host
    server.api_url = data.api_url
    server.api_token = data.api_token
    server.wireguard_inbound_id = data.wireguard_inbound_id
    server.priority = data.priority
    server.enabled = data.enabled


    server_repo.update(
        server
    )


    return {
        "status": "updated",
        "id": server.id,
    }



@router.post(
    "/servers/{server_id}/enable"
)
async def enable_admin_server(
    server_id: int,
    user: User = Depends(get_current_user),
):

    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    try:

        server = server_service.enable_server(
            server_id
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return {
        "status": "enabled",
        "id": server.id,
    }

@router.post(
    "/servers/{server_id}/disable"
)
async def disable_admin_server(
    server_id: int,
    user: User = Depends(get_current_user),
):

    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    try:

        server = server_service.disable_server(
            server_id
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return {
        "status": "disabled",
        "id": server.id,
    }

@router.delete(
    "/servers/{server_id}"
)
async def delete_admin_server(
    server_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    try:

        server_service.delete_server(
            server_id
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=409,
            detail=str(e),
        )


    return {
        "status": "deleted",
        "id": server_id,
    }


@router.post("/users/{user_id}/block")
async def block_user_endpoint(
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


    result = await admin_service.block_user(
        user_id
    )


    if result is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return {
        "success": True,
        "user_id": user_id,
        "blocked": True,
    }


@router.post("/users/{user_id}/unblock")
async def unblock_user_endpoint(
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


    result = await admin_service.unblock_user(
        user_id
    )


    if result is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return {
        "success": True,
        "user_id": user_id,
        "blocked": False,
    }



@router.get(
    "/users/statistics",
)
async def get_users_statistics(
    user: User = Depends(
        get_current_user
    ),
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


    return admin_service.get_users_statistics()
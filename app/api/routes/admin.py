from decimal import Decimal, ROUND_HALF_UP
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.api.dependencies.admin import (
    get_current_admin,
)

from app.api.schemas.admin import (
    AdminBalanceAdjustRequest,
    AdminBalanceAdjustResponse,
    AdminSubscriptionResponse,
    AdminSubscriptionExtendRequest,
    AdminSubscriptionExtendResponse,
    AdminUserBlockResponse,
    AdminUserDetailResponse,
    AdminUserListItem,
    AdminUsersResponse,
)

from app.domain.user import User

from app.repositories.user_repository import (
    users_repo,
)

from app.repositories.wallet_repository import (
    wallet_repo,
)

from app.repositories.subscription_repository import (
    subscription_repo,
)


from app.services.vpn_service import (
    vpn_service,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


def _status_value(status) -> str:

    value = getattr(
        status,
        "value",
        None,
    )

    if value is not None:
        return str(value)

    return str(status)


def _subscription_response(
    subscription,
) -> AdminSubscriptionResponse:

    return AdminSubscriptionResponse(
        id=subscription.id,
        protocol=subscription.protocol,
        provider=subscription.provider,
        status=_status_value(
            subscription.status
        ),
        server_id=subscription.server_id,
        client_email=subscription.client_email,
        device_limit=subscription.device_limit,
        billing_mode=subscription.billing_mode,
        billing_enabled=subscription.billing_enabled,
        created_at=subscription.created_at,
        expires_at=subscription.expires_at,
        paid_until=subscription.paid_until,
            bonus_until=subscription.bonus_until,
    )


def _latest_subscription(
    user_id: int,
):

    subscriptions = (
        subscription_repo.get_by_user(
            user_id
        )
    )

    if not subscriptions:
        return None

    return subscriptions[0]


def _user_list_item(
    user,
) -> AdminUserListItem:

    if user.id is None:
        raise ValueError(
            "User has no id"
        )

    balance_kopecks = (
        wallet_repo.get_balance(
            user.id
        )
    )

    subscription = (
        _latest_subscription(
            user.id
        )
    )

    return AdminUserListItem(
        id=user.id,
        telegram_id=user.telegram_id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        is_admin=user.is_admin,
        is_blocked=user.is_blocked,
        balance_kopecks=balance_kopecks,
        balance_rubles=(
            balance_kopecks / 100
        ),
        subscription=(
            _subscription_response(
                subscription
            )
            if subscription
            else None
        ),
    )


def _matches_filter(
    user,
    status_filter: str,
) -> bool:

    if status_filter == "all":
        return True

    if status_filter == "blocked":
        return bool(
            user.is_blocked
        )

    if status_filter == "admins":
        return bool(
            user.is_admin
        )

    if user.id is None:
        return False

    subscriptions = (
        subscription_repo.get_by_user(
            user.id
        )
    )

    if status_filter == "no_subscription":
        return len(
            subscriptions
        ) == 0

    statuses = {
        _status_value(
            subscription.status
        )
        for subscription in subscriptions
    }

    if status_filter == "active":
        return "active" in statuses

    if status_filter == "expired":
        return "expired" in statuses

    if status_filter == "disabled":
        return "disabled" in statuses

    return True


@router.get(
    "/users",
    response_model=AdminUsersResponse,
)
async def admin_users(
    search: str | None = Query(
        default=None,
    ),
    status_filter: Literal[
        "all",
        "active",
        "expired",
        "disabled",
        "blocked",
        "admins",
        "no_subscription",
    ] = Query(
        default="all",
        alias="filter",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    _admin: User = Depends(
        get_current_admin
    ),
):

    query = (
        search.strip()
        if search
        else ""
    )

    if query:

        users = users_repo.search(
            query
        )

    else:

        users = users_repo.get_all()

    filtered_users = [
        user
        for user in users
        if _matches_filter(
            user,
            status_filter,
        )
    ]

    total = len(
        filtered_users
    )

    page = filtered_users[
        offset:offset + limit
    ]

    return AdminUsersResponse(
        items=[
            _user_list_item(
                user
            )
            for user in page
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse,
)
async def admin_user_detail(
    user_id: int,
    _admin: User = Depends(
        get_current_admin
    ),
):

    user = users_repo.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    subscriptions = (
        subscription_repo.get_by_user(
            user_id
        )
    )

    balance_kopecks = (
        wallet_repo.get_balance(
            user_id
        )
    )

    transactions = (
        wallet_repo.get_transactions(
            user_id=user_id,
            limit=100,
        )
    )

    return AdminUserDetailResponse(
        id=user_id,
        telegram_id=user.telegram_id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        is_admin=user.is_admin,
        is_blocked=user.is_blocked,
        balance_kopecks=balance_kopecks,
        balance_rubles=(
            balance_kopecks / 100
        ),
        subscriptions=[
            _subscription_response(
                subscription
            )
            for subscription
            in subscriptions
        ],
        wallet_transactions=transactions,
    )


@router.post(
    "/users/{user_id}/balance",
    response_model=AdminBalanceAdjustResponse,
)
async def admin_adjust_balance(
    user_id: int,
    request: AdminBalanceAdjustRequest,
    admin: User = Depends(
        get_current_admin
    ),
):

    user = users_repo.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    amount = (
        request.amount_rubles
        .quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    )

    if amount <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Amount must be greater "
                "than zero"
            ),
        )

    amount_kopecks = int(
        amount * 100
    )

    admin_name = (
        f"admin:{admin.id}"
    )

    description = (
        request.description.strip()
        if request.description
        else None
    )

    if description:

        transaction_description = (
            f"{description} "
            f"({admin_name})"
        )

    else:

        transaction_description = (
            f"Manual balance adjustment "
            f"({admin_name})"
        )

    if request.action == "credit":

        new_balance = wallet_repo.credit(
            user_id=user_id,
            amount_kopecks=amount_kopecks,
            transaction_type=(
                "admin_credit"
            ),
            description=(
                transaction_description
            ),
        )

    else:

        new_balance = wallet_repo.debit(
            user_id=user_id,
            amount_kopecks=amount_kopecks,
            transaction_type=(
                "admin_debit"
            ),
            description=(
                transaction_description
            ),
        )

        if new_balance is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Insufficient balance"
                ),
            )

    return AdminBalanceAdjustResponse(
        user_id=user_id,
        action=request.action,
        amount_kopecks=(
            amount_kopecks
        ),
        amount_rubles=(
            amount_kopecks / 100
        ),
        balance_kopecks=(
            new_balance
        ),
        balance_rubles=(
            new_balance / 100
        ),
    )


@router.post(
    "/users/{user_id}/block",
    response_model=AdminUserBlockResponse,
)
async def admin_block_user(
    user_id: int,
    admin: User = Depends(
        get_current_admin
    ),
):

    user = users_repo.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if admin.id == user_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "You cannot block yourself"
            ),
        )

    users_repo.block(
        user_id
    )

    return AdminUserBlockResponse(
        user_id=user_id,
        is_blocked=True,
    )


@router.post(
    "/users/{user_id}/unblock",
    response_model=AdminUserBlockResponse,
)
async def admin_unblock_user(
    user_id: int,
    _admin: User = Depends(
        get_current_admin
    ),
):

    user = users_repo.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    users_repo.unblock(
        user_id
    )

    return AdminUserBlockResponse(
        user_id=user_id,
        is_blocked=False,
    )


@router.post(
    "/users/{user_id}/subscriptions/"
    "{subscription_id}/extend",
    response_model=(
        AdminSubscriptionExtendResponse
    ),
)
async def admin_extend_subscription(
    user_id: int,
    subscription_id: int,
    request: AdminSubscriptionExtendRequest,
    _admin: User = Depends(
        get_current_admin
    ),
):

    if request.days < 1:
        raise HTTPException(
            status_code=400,
            detail="Days must be greater than 0",
        )

    if request.days > 3650:
        raise HTTPException(
            status_code=400,
            detail="Maximum allowed: 3650 days",
        )

    subscription = (
        subscription_repo.get_by_id(
            subscription_id
        )
    )

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    if subscription.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    try:

        updated = (
            await vpn_service
            .admin_extend_subscription(
                subscription=subscription,
                days=request.days,
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=(
                "Не удалось обновить "
                "подписку в Remnawave"
            ),
        ) from error

    return (
        AdminSubscriptionExtendResponse(
            subscription_id=updated.id,
            user_id=updated.user_id,
            days_added=request.days,
            status=_status_value(
                updated.status
            ),
            expires_at=updated.expires_at,
        )
    )


@router.post(
    "/users/{user_id}/subscriptions/"
    "{subscription_id}/bonus/remove"
)
async def admin_remove_subscription_bonus(
    user_id: int,
    subscription_id: int,
    days: int | None = None,
    remove_all: bool = False,
    _admin: User = Depends(
        get_current_admin
    ),
):
    from datetime import (
        datetime,
        timedelta,
        timezone,
    )

    from app.database.database import db
    from app.services.billing_service import (
        billing_service,
    )

    subscription = (
        subscription_repo.get_by_id(
            subscription_id
        )
    )

    if (
        subscription is None
        or subscription.user_id != user_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    now = datetime.now(
        timezone.utc
    )

    bonus_until = (
        subscription.bonus_until
    )

    if bonus_until is None:
        return {
            "subscription_id": subscription.id,
            "removed_days": 0,
            "bonus_until": None,
        }

    if bonus_until.tzinfo is None:
        bonus_until = (
            bonus_until.replace(
                tzinfo=timezone.utc
            )
        )

    if bonus_until <= now:
        db.execute(
            """
            UPDATE subscriptions
            SET bonus_until = NULL
            WHERE id = ?
            """,
            (
                subscription.id,
            ),
        )

        return {
            "subscription_id": subscription.id,
            "removed_days": 0,
            "bonus_until": None,
        }

    remaining_seconds = int(
        (
            bonus_until - now
        ).total_seconds()
    )

    if remove_all:
        remove_seconds = (
            remaining_seconds
        )
    else:
        if days is None or days < 1:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Days must be greater than 0"
                ),
            )

        remove_seconds = min(
            remaining_seconds,
            days * 86400,
        )

    delta = timedelta(
        seconds=remove_seconds
    )

    new_bonus_until = (
        bonus_until - delta
    )

    if new_bonus_until <= now:
        new_bonus_until = None

    paid_until = (
        subscription.paid_until
        or now
    )

    if paid_until.tzinfo is None:
        paid_until = (
            paid_until.replace(
                tzinfo=timezone.utc
            )
        )

    new_paid_until = (
        paid_until - delta
    )

    if new_paid_until < now:
        new_paid_until = now

    db.execute(
        """
        UPDATE subscriptions
        SET
            paid_until = ?,
            bonus_until = ?
        WHERE id = ?
        """,
        (
            int(
                new_paid_until.timestamp()
            ),
            (
                int(
                    new_bonus_until.timestamp()
                )
                if new_bonus_until
                else None
            ),
            subscription.id,
        ),
    )

    # Пересчитываем expires_at с учётом
    # текущего баланса и обновляем Remnawave.
    await billing_service.refresh_balance_expiry(
        subscription.id
    )

    updated = (
        subscription_repo.get_by_id(
            subscription.id
        )
    )

    removed_days = (
        remove_seconds / 86400
    )

    return {
        "subscription_id": subscription.id,
        "removed_days": removed_days,
        "bonus_until": (
            updated.bonus_until.isoformat()
            if (
                updated
                and updated.bonus_until
            )
            else None
        ),
        "paid_until": (
            updated.paid_until.isoformat()
            if (
                updated
                and updated.paid_until
            )
            else None
        ),
        "expires_at": (
            updated.expires_at.isoformat()
            if (
                updated
                and updated.expires_at
            )
            else None
        ),
    }


@router.post(
    "/users/{user_id}/subscriptions/"
    "{subscription_id}/set-until"
)
async def admin_set_subscription_until(
    user_id: int,
    subscription_id: int,
    until: str,
    admin: User = Depends(
        get_current_admin
    ),
):
    from datetime import (
        date,
        datetime,
        time,
        timezone,
    )

    subscription = (
        subscription_repo.get_by_id(
            subscription_id
        )
    )

    if (
        subscription is None
        or subscription.user_id != user_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    try:
        target_date = date.fromisoformat(
            until
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date",
        )

    target_at = datetime.combine(
        target_date,
        time(23, 59, 59),
        tzinfo=timezone.utc,
    )

    try:
        updated = (
            await vpn_service
            .admin_set_subscription_until(
                subscription,
                target_at,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "subscription_id": updated.id,
        "user_id": updated.user_id,
        "status": (
            updated.status.value
            if hasattr(
                updated.status,
                "value",
            )
            else str(updated.status)
        ),
        "paid_until": (
            updated.paid_until.isoformat()
            if updated.paid_until
            else None
        ),
        "expires_at": (
            updated.expires_at.isoformat()
            if updated.expires_at
            else None
        ),
    }

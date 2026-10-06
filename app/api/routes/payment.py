from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends,
)

from pydantic import BaseModel, Field

from app.logger import logger

from app.services.payment_service import (
    payment_service,
    PaymentProviderError,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User

from app.repositories.wallet_repository import (
    wallet_repo,
)

from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.services.pricing_service import (
    get_daily_price_kopecks,
    MAX_DEVICE_LIMIT,
    TRIAL_DEVICE_LIMIT,
)


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


class BalanceTopupRequest(BaseModel):
    amount: int = Field(
        ge=10,
        le=10000,
    )




@router.get(
    "/wallet"
)
async def get_wallet(
    user: User = Depends(
        get_current_user
    ),
):
    balance_kopecks = (
        wallet_repo.get_balance(
            user.id
        )
    )

    subscriptions = (
        subscription_repo.get_by_user(
            user.id
        )
    )

    balance_subscription = next(
        (
            subscription
            for subscription
            in subscriptions
            if (
                subscription.billing_mode
                == "balance"
                and subscription.status.value
                != "deleted"
            )
        ),
        None,
    )

    device_limit = (
        balance_subscription.device_limit
        if balance_subscription
        else TRIAL_DEVICE_LIMIT
    )

    daily_price_kopecks = (
        get_daily_price_kopecks(
            device_limit
        )
    )

    return {
        "balance_kopecks": (
            balance_kopecks
        ),
        "balance_rubles": (
            balance_kopecks / 100
        ),
        "device_limit": (
            device_limit
        ),
        "daily_price_kopecks": (
            daily_price_kopecks
        ),
        "daily_price_rubles": (
            daily_price_kopecks / 100
        ),
        "days_available": (
            balance_kopecks
            // daily_price_kopecks
        ),
        "max_devices": (
            MAX_DEVICE_LIMIT
        ),
    }


@router.get(
    "/history"
)
async def get_wallet_history(
    user: User = Depends(
        get_current_user
    ),
):
    transactions = (
        wallet_repo.get_transactions(
            user_id=user.id,
            limit=50,
        )
    )

    return {
        "items": transactions,
    }


@router.post(
    "/topup"
)
async def create_balance_topup(
    request: BalanceTopupRequest,
    user: User = Depends(
        get_current_user
    ),
):
    try:
        payment = await payment_service.create_balance_topup(
            user_id=user.id,
            amount_rubles=request.amount,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PaymentProviderError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Платёжный сервис временно недоступен. "
                "Попробуйте ещё раз позже."
            ),
        )

    return {
        "payment_id": payment.id,
        "provider_payment_id": (
            payment.provider_payment_id
        ),
        "confirmation_url": (
            payment.confirmation_url
        ),
        "amount": payment.amount,
        "amount_kopecks": (
            payment.amount_kopecks
        ),
        "currency": payment.currency,
        "status": (
            payment.status.value
            if hasattr(
                payment.status,
                "value",
            )
            else payment.status
        ),
    }


@router.post(
    "/webhook"
)
async def webhook(
    request: Request,
):

    try:

        data = await request.json()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid JSON",
        )


    logger.info(
        "YooKassa webhook received"
    )


    event = data.get(
        "event"
    )


    if event != "payment.succeeded":

        logger.info(
            f"Ignore YooKassa event: {event}"
        )

        return {
            "status": "ignored"
        }


    payment_object = data.get(
        "object",
        {}
    )


    provider_payment_id = payment_object.get(
        "id"
    )


    if provider_payment_id is None:

        logger.warning(
            "YooKassa payment id missing"
        )

        return {
            "status": "error"
        }



    payment = await payment_service.process_successful_payment(
        provider_payment_id
    )


    if payment is None:

        logger.warning(
            f"Payment not found: {provider_payment_id}"
        )

        return {
            "status": "not_found"
        }



    logger.success(
        f"Payment completed: {provider_payment_id}"
    )


    return {
        "status": "ok"
    }
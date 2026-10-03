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
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


class BalanceTopupRequest(BaseModel):
    amount: int = Field(
        ge=10,
        le=10000,
    )




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
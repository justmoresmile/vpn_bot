from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.api.dependencies.internal import (
    verify_internal_api_key,
)

from app.api.schemas.purchase import (
    PurchaseResponse,
    InternalPurchaseRequest,
)

from app.services.payment_service import (
    payment_service,
)

from app.logger import logger


router = APIRouter(
    prefix="/internal",
    tags=["Internal"],
    dependencies=[
        Depends(verify_internal_api_key),
    ],
)


@router.post(
    "/purchase",
    response_model=PurchaseResponse,
)
async def create_purchase(
    request: InternalPurchaseRequest,
):

    logger.info(
        "Internal purchase request: telegram_id=%s protocol=%s days=%s",
        request.telegram_id,
        request.protocol,
        request.days,
    )


    payment = await payment_service.create_payment_by_telegram(
        telegram_id=request.telegram_id,
        protocol=request.protocol,
        days=request.days,
    )


    if payment is None:

        logger.warning(
            "User not found: telegram_id=%s",
            request.telegram_id,
        )

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    logger.success(
        "Payment created: id=%s provider=%s",
        payment.id,
        payment.provider_payment_id,
    )


    return PurchaseResponse(

        payment_id=payment.id,

        provider_payment_id=(
            payment.provider_payment_id
        ),

        confirmation_url=(
            payment.confirmation_url
        ),

        amount=(
            payment.amount
        ),

        currency=(
            payment.currency
        ),

        status=(
            payment.status.value
            if hasattr(payment.status, "value")
            else payment.status
        ),
    )
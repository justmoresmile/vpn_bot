from fastapi import (
APIRouter,
Depends,
HTTPException,
)

from app.api.schemas.purchase import (
PurchaseResponse,
PurchaseRequest,
)

from app.services.payment_service import (
payment_service,
)

from app.api.dependencies.auth import (
get_current_user,
)

from app.domain.user import User

router = APIRouter(
prefix="/purchase",
tags=["Purchase"],
)

@router.post(
"/",
response_model=PurchaseResponse,
)
async def create_purchase(
    request: PurchaseRequest,
    user: User = Depends(
    get_current_user
    ),
    ):


    protocol = "vless"

    payment = await payment_service.create_payment_by_telegram(
        telegram_id=user.telegram_id,
        protocol=protocol,
        days=request.days,
        subscription_id=request.subscription_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=400,
            detail="Payment creation failed",
        )

    return PurchaseResponse(
        payment_id=payment.id,
        provider_payment_id=(
            payment.provider_payment_id
        ),
        confirmation_url=(
            payment.confirmation_url
        ),
        amount=payment.amount,
        currency=payment.currency,
        status=(
            payment.status.value
            if hasattr(
                payment.status,
                "value",
            )
            else payment.status
        ),
    )


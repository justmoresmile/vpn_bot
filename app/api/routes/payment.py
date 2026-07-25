from fastapi import (
    APIRouter,
    Request,
    HTTPException,
)

from app.logger import logger

from app.services.payment_service import (
    payment_service,
)


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)



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
from fastapi import APIRouter, Request

from app.logger import logger
from app.services.payment_service import payment_service


router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("/yookassa/webhook")
async def yookassa_webhook(
    request: Request,
):

    data = await request.json()

    logger.info(
        f"YooKassa webhook received: {data}"
    )


    event = data.get("event")


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


    if not provider_payment_id:

        logger.warning(
            "Webhook without payment id"
        )

        return {
            "status": "error"
        }


    await payment_service.process_successful_payment(
        provider_payment_id
    )


    return {
        "status": "ok"
    }
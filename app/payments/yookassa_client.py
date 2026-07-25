import uuid

from yookassa import Configuration, Payment

from app.config import settings


class YooKassaClient:

    def __init__(self):

        Configuration.account_id = (
            settings.yookassa_shop_id
        )

        Configuration.secret_key = (
            settings.yookassa_secret_key
        )

        # ВАЖНО
        Configuration.verify = False


    def create_payment(
        self,
        amount: float,
        description: str,
    ):

        payment = Payment.create(
            {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": (
                        settings.payment_return_url
                    ),
                },
                "capture": True,
                "description": description,
            },
            uuid.uuid4().hex,
        )


        return payment


yookassa_client = YooKassaClient()
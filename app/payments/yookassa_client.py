import uuid

from yookassa import Configuration, Payment

from app.config import settings


Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key


class YooKassaClient:

    @staticmethod
    def create_payment(
        amount: float,
        description: str,
    ):

        payment = Payment.create(
            {
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.payment_return_url,
                },
                "capture": True,
                "description": description,
            },
            uuid.uuid4().hex,
        )

        return payment

    @staticmethod
    def get_payment(payment_id: str):
        return Payment.find_one(payment_id)

    @staticmethod
    def cancel_payment(payment_id: str):
        return Payment.cancel(payment_id)


yookassa_client = YooKassaClient()
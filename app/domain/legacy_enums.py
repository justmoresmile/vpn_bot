from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


class PaymentProvider(StrEnum):
    TELEGRAM = "telegram"
    YOOKASSA = "yookassa"
    CRYPTOBOT = "cryptobot"
    STRIPE = "stripe"

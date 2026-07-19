from enum import StrEnum


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    EXPIRED = "expired"


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
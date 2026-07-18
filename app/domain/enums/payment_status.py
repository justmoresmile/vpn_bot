from enum import StrEnum


class PaymentStatus(StrEnum):

    PENDING = "pending"

    PAID = "paid"

    FAILED = "failed"

    CANCELED = "canceled"
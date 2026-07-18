from enum import StrEnum


class SubscriptionStatus(StrEnum):

    ACTIVE = "active"

    DISABLED = "disabled"

    EXPIRED = "expired"
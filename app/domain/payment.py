from dataclasses import dataclass
from datetime import datetime


@dataclass
class Payment:

    id: int | None

    user_id: int

    protocol: str

    subscription_days: int

    amount: float
    currency: str

    provider: str

    provider_payment_id: str | None

    confirmation_url: str | None

    status: str

    created_at: datetime

    paid_at: datetime | None
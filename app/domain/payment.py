from dataclasses import dataclass
from datetime import datetime


@dataclass
class Payment:

    id: int | None

    user_id: int

    subscription_id: int | None

    protocol: str

    subscription_days: int

    amount: float

    currency: str

    status: str

    provider: str

    provider_payment_id: str | None

    confirmation_url: str | None

    created_at: datetime

    paid_at: datetime | None

    updated_at: datetime | None
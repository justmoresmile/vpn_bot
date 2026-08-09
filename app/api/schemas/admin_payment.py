from datetime import datetime

from pydantic import BaseModel


class AdminPaymentResponse(BaseModel):

    id: int

    telegram_id: int

    username: str | None

    first_name: str | None

    subscription_id: int | None

    client_email: str | None

    protocol: str

    subscription_days: int

    amount: float

    currency: str

    status: str

    provider: str

    created_at: datetime

    paid_at: datetime | None
from datetime import datetime

from pydantic import BaseModel


class PaymentResponse(BaseModel):

    id: int

    amount: float

    currency: str

    protocol: str

    subscription_days: int

    status: str

    created_at: datetime

    paid_at: datetime | None
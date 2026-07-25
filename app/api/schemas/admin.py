from datetime import datetime

from pydantic import BaseModel


class AdminUserCardResponse(BaseModel):
    id: int

    telegram_id: int

    username: str | None

    first_name: str | None

    created_at: datetime

    is_admin: bool

    subscriptions_count: int

    payments_count: int

    total_paid: int
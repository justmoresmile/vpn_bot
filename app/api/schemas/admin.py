from datetime import datetime

from pydantic import BaseModel


class AdminUserCardResponse(BaseModel):

    id: int

    telegram_id: int

    username: str | None

    first_name: str | None

    created_at: datetime

    is_admin: bool


    subscriptions: list[dict] = []


    subscriptions_count: int

    payments_count: int

    total_paid: int


    active_subscriptions: int

    expired_subscriptions: int

    disabled_subscriptions: int


    current_subscription: dict | None = None

    last_payment: dict | None = None

    days_left: int | None = None

    vpn: dict | None = None
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class User:

    id: int | None

    telegram_id: int | None

    email: str | None

    username: str | None

    first_name: str | None

    is_admin: bool = False

    is_blocked: bool = False

    api_key: str | None = None

    vpn_provider: str | None = None
    provider_user_id: int | None = None
    provider_username: str | None = None

    created_at: datetime | None = None

    subscriptions_count: int = 0

    payments_count: int = 0

    total_paid: int = 0

    trial_used: bool = False
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None

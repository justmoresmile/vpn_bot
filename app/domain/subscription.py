from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.subscription_status import SubscriptionStatus


@dataclass
class Subscription:

    id: int | None

    user_id: int
    protocol: str

    # VPN provider
    provider: str = "remnawave"

    # Legacy / provider-specific fields.
    # Для Remnawave они могут быть None.
    server_id: int | None = None
    inbound_id: int | None = None

    client_id: str | None = None
    client_email: str | None = None

    subscription_token: str | None = None

    sub_id: str | None = None

    config: str = ""

    status: SubscriptionStatus = (
        SubscriptionStatus.ACTIVE
    )

    device_limit: int = 2

    created_at: datetime | None = None
    expires_at: datetime | None = None

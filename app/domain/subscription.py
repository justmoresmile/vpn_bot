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

    device_limit: int = 1

    # После изменения тарифа повторная смена
    # запрещена до следующего расчётного периода.
    device_limit_locked_until: datetime | None = None

    created_at: datetime | None = None
    expires_at: datetime | None = None

    # Billing
    billing_mode: str = "fixed"
    paid_until: datetime | None = None
    billing_day_index: int = 0
    billing_enabled: bool = True

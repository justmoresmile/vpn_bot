from dataclasses import dataclass
from datetime import datetime

from app.domain.enums.subscription_status import SubscriptionStatus


@dataclass
class Subscription:

    id: int | None

    user_id: int
    server_id: int
    protocol: str
    inbound_id: int

    client_id: str
    client_email: str

    # Короткий токен нашей подписки
    subscription_token: str | None = None

    # Используется только VLESS.
    # Для WireGuard остается None.
    sub_id: str | None = None

    config: str = ""

    status: SubscriptionStatus = SubscriptionStatus.ACTIVE

    # Максимальное количество устройств
    # для этой конкретной подписки.
    device_limit: int = 2

    created_at: datetime | None = None
    expires_at: datetime | None = None
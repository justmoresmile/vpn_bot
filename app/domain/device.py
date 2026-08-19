from dataclasses import dataclass
from datetime import datetime


@dataclass
class Device:

    id: int | None

    subscription_id: int

    device_token: str

    device_name: str | None = None

    device_model: str | None = None

    device_os: str | None = None

    os_version: str | None = None

    is_active: bool = True

    first_seen_at: datetime | None = None

    last_seen_at: datetime | None = None
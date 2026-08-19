from dataclasses import dataclass
from datetime import datetime


@dataclass
class DeviceClient:

    id: int | None

    device_id: int

    client_app: str | None

    client_version: str | None

    client_identifier: str

    first_seen_at: datetime | None = None

    last_seen_at: datetime | None = None
from dataclasses import dataclass
from datetime import datetime

@dataclass(slots=True, frozen=True)
class User:
    id: int | None

    telegram_id: int

    username: str | None
    first_name: str | None

    is_admin: bool = False
    api_key: str | None = None
    created_at: datetime | None = None
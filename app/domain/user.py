from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class User:
    id: int | None

    telegram_id: int

    username: str | None
    first_name: str | None

    is_admin: bool = False
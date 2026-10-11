from dataclasses import dataclass
from datetime import datetime


@dataclass
class SupportTicket:

    id: int | None

    user_id: int

    subject: str

    category: str | None = None

    status: str = "open"

    created_at: datetime | None = None

    updated_at: datetime | None = None

    closed_at: datetime | None = None

    telegram_thread_id: int | None = None


@dataclass
class SupportMessage:

    id: int | None

    ticket_id: int

    sender_type: str

    sender_id: int | None

    message: str

    is_read: bool = False

    created_at: datetime | None = None

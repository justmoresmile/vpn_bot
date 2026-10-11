from datetime import datetime

from pydantic import BaseModel, Field


class SupportTicketCreateRequest(BaseModel):

    subject: str = Field(
        min_length=1,
        max_length=120,
    )

    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    category: str | None = None


class SupportMessageCreateRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=4000,
    )


class SupportMessageResponse(BaseModel):

    id: int

    ticket_id: int

    sender_type: str

    sender_id: int | None

    message: str

    is_read: bool

    created_at: datetime


class SupportTicketResponse(BaseModel):

    id: int

    user_id: int

    subject: str

    category: str | None

    status: str

    created_at: datetime

    updated_at: datetime

    closed_at: datetime | None


class SupportTicketDetailsResponse(
    SupportTicketResponse
):

    messages: list[
        SupportMessageResponse
    ]

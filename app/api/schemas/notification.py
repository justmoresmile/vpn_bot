from pydantic import BaseModel


class NotificationResponse(BaseModel):

    id: int
    type: str
    title: str
    message: str
    related_type: str | None
    related_id: int | None
    is_read: bool
    created_at: int


class NotificationUnreadResponse(BaseModel):

    count: int

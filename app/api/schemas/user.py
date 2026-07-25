from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    is_admin: bool

class SyncUserRequest(BaseModel):

    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class SyncUserResponse(BaseModel):

    created: bool
    id: int
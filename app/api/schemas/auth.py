from pydantic import BaseModel


class TelegramWebAppAuthRequest(BaseModel):
    init_data: str


class TelegramWebAppAuthResponse(BaseModel):
    access_token: str
    token_type: str
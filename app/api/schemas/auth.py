from pydantic import BaseModel, Field


class TelegramWebAppAuthRequest(BaseModel):
    init_data: str


class TelegramWebAppAuthResponse(BaseModel):
    access_token: str
    token_type: str


class EmailCodeRequest(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=254,
    )


class EmailCodeRequestResponse(BaseModel):
    success: bool
    expires_in: int


class EmailCodeVerifyRequest(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=254,
    )

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class EmailCodeVerifyResponse(BaseModel):
    access_token: str
    token_type: str
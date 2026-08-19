from datetime import datetime

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):

    id: int

    user_id: int

    protocol: str

    status: str

    expires_at: datetime

    client_email: str


class SubscriptionShortResponse(BaseModel):

    id: int

    protocol: str

    status: str

    expires_at: datetime

    client_email: str | None = None

    server_name: str | None = None

    server_country: str | None = None


class ConfigResponse(BaseModel):

    config: str


class RenewResponse(BaseModel):

    id: int

    status: str

    expires_at: datetime


class SubscriptionUsageResponse(BaseModel):

    up: int

    down: int

    total: int

class SubscriptionDeviceResponse(BaseModel):

    id: int

    model: str | None = None

    os: str | None = None

    os_version: str | None = None

    client_app: str | None = None

    client_version: str | None = None

    is_active: bool

    last_seen_at: datetime


class SubscriptionDevicesResponse(BaseModel):

    count: int

    limit: int

    devices: list[
        SubscriptionDeviceResponse
    ]
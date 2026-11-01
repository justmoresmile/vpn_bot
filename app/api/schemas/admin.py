from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class AdminSubscriptionResponse(BaseModel):
    id: int
    protocol: str
    provider: str
    status: str

    server_id: int | None = None
    client_email: str | None = None

    device_limit: int

    billing_mode: str
    billing_enabled: bool

    created_at: datetime | None = None
    expires_at: datetime | None = None
    paid_until: datetime | None = None
    bonus_until: datetime | None = None
    bonus_device_limit: int | None = None


class AdminUserListItem(BaseModel):
    id: int

    telegram_id: int | None
    email: str | None

    username: str | None
    first_name: str | None

    is_admin: bool
    is_blocked: bool

    balance_kopecks: int
    balance_rubles: float

    subscription: AdminSubscriptionResponse | None = None


class AdminUsersResponse(BaseModel):
    items: list[AdminUserListItem]

    total: int
    limit: int
    offset: int


class AdminUserDetailResponse(BaseModel):
    id: int

    telegram_id: int | None
    email: str | None

    username: str | None
    first_name: str | None

    is_admin: bool
    is_blocked: bool

    balance_kopecks: int
    balance_rubles: float

    subscriptions: list[AdminSubscriptionResponse]

    wallet_transactions: list[dict]


class AdminBalanceAdjustRequest(BaseModel):
    action: Literal[
        "credit",
        "debit",
    ]

    amount_rubles: Decimal

    description: str | None = None


class AdminBalanceAdjustResponse(BaseModel):
    user_id: int

    action: str

    amount_kopecks: int
    amount_rubles: float

    balance_kopecks: int
    balance_rubles: float


class AdminUserBlockResponse(BaseModel):
    user_id: int
    is_blocked: bool


class AdminSubscriptionExtendRequest(BaseModel):
    days: int


class AdminSubscriptionExtendResponse(BaseModel):
    subscription_id: int
    user_id: int
    days_added: int
    status: str
    expires_at: datetime

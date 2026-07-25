from pydantic import BaseModel


class PurchaseRequest(BaseModel):
    protocol: str = "wireguard"
    days: int = 30
    subscription_id: int | None = None


class InternalPurchaseRequest(BaseModel):
    telegram_id: int
    protocol: str = "wireguard"
    days: int = 30
    subscription_id: int | None = None


class PurchaseResponse(BaseModel):
    payment_id: int
    provider_payment_id: str | None
    confirmation_url: str | None
    amount: int | float
    currency: str
    status: str
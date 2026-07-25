from datetime import datetime

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):

    id: int

    user_id: int

    protocol: str

    status: str

    expires_at: datetime



class SubscriptionShortResponse(BaseModel):

    id: int

    protocol: str

    status: str

    expires_at: datetime



class ConfigResponse(BaseModel):

    config: str



class RenewResponse(BaseModel):

    id: int

    status: str

    expires_at: datetime
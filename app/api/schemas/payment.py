from pydantic import BaseModel


class PaymentResponse(BaseModel):
    status: str
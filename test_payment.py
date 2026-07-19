import app.bootstrap

from app.payments.yookassa_client import yookassa_client

from app.payments.yookassa_client import yookassa_client

payment = yookassa_client.create_payment(
    amount=100,
    description="Тест VPN",
)

print(payment.confirmation.confirmation_url)

payment = yookassa_client.create_payment(
    amount=100,
    description="Тест VPN",
)

print(payment.id)
print(payment.status)
print(payment.confirmation.confirmation_url)
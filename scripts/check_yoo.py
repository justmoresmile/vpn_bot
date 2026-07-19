import app.bootstrap
from app.payments.yookassa_client import yookassa_client


payment = yookassa_client.get_payment(
    "31eec69a-000f-5001-9000-1f0bf973bf3d"
)


print(payment.status)
print(payment.paid)
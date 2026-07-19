from datetime import datetime

from app.domain.payment import Payment
from app.domain.enums.payment_status import PaymentStatus

from app.repositories.payment_repository import payment_repo
from app.payments.yookassa_client import yookassa_client
from app.services.vpn_service import vpn_service


class PaymentService:


    PRICES = {
        30: 299,
        90: 799,
        180: 1499,
        365: 2499,
    }


    def calculate_price(
        self,
        days: int,
    ) -> float:

        price = self.PRICES.get(days)

        if price is None:
            raise ValueError(
                f"Unsupported days: {days}"
            )

        return price



    def create_payment(
        self,
        user_id: int,
        protocol: str,
        days: int,
    ) -> Payment:


        amount = self.calculate_price(
            days
        )


        payment = yookassa_client.create_payment(
            amount=amount,
            description=(
                f"VPN {protocol.upper()} "
                f"{days} дней"
            ),
        )


        entity = Payment(

            id=None,

            user_id=user_id,

            protocol=protocol,

            subscription_days=days,

            amount=amount,

            currency="RUB",

            provider="yookassa",

            provider_payment_id=payment.id,

            confirmation_url=(
                payment.confirmation.confirmation_url
                if payment.confirmation
                else None
            ),

            status=PaymentStatus.PENDING,

            created_at=datetime.now(),

            paid_at=None,
        )


        return payment_repo.create(
            entity
        )



    def get_payment(
        self,
        payment_id: int,
    ) -> Payment | None:

        return payment_repo.get_by_id(
            payment_id
        )



    def get_by_provider_id(
        self,
        provider_payment_id: str,
    ) -> Payment | None:

        return (
            payment_repo
            .get_by_provider_payment_id(
                provider_payment_id
            )
        )



    async def process_successful_payment(
        self,
        provider_payment_id: str,
    ) -> Payment | None:


        payment = (
            self.get_by_provider_id(
                provider_payment_id
            )
        )


        if payment is None:
            return None



        if payment.status == PaymentStatus.PAID:
            return payment



        # отмечаем оплату

        payment_repo.mark_paid(
            payment.id
        )



        # получаем обновлённый объект

        payment = (
            self.get_payment(
                payment.id
            )
        )



        # создаём VPN

        await vpn_service.purchase(

            user_id=payment.user_id,

            protocol=payment.protocol,

            days=payment.subscription_days,

        )


        return payment
    
    async def check_payment(
        self,
        provider_payment_id: str,
    ) -> bool:

        payment = yookassa_client.get_payment(
            provider_payment_id
        )

        if payment.status != "succeeded":
            return False

        await self.process_successful_payment(
            provider_payment_id
        )

        return True


payment_service = PaymentService()
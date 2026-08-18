from datetime import datetime

from loguru import logger

from app.domain.payment import Payment
from app.domain.enums.payment_status import PaymentStatus

from app.repositories.payment_repository import payment_repo
from app.payments.yookassa_client import yookassa_client
from app.services.vpn_service import vpn_service
from app.repositories.user_repository import users_repo
from app.services.subscription_service import subscription_service


class PaymentService:


    PRICES = {
        30: 150,
        90: 420,
        180: 800,
        365: 1500,
    }


    def calculate_price(
        self,
        days: int,
    ) -> float:

        price = self.PRICES.get(
            days
        )

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
        subscription_id: int | None = None,
    ) -> Payment:

        amount = self.calculate_price(
            days
        )

        existing = payment_repo.get_pending_by_user_tariff(
            user_id=user_id,
            protocol=protocol,
            subscription_days=days,
            subscription_id=subscription_id,
        )

        if existing:

            logger.info(
                f"Reuse pending payment {existing.id}"
            )

            return existing

        payment = yookassa_client.create_payment(
            amount=amount,
            description=f"VPN {protocol.upper()} {days} дней",
        )

        entity = Payment(
            id=None,
            user_id=user_id,
            subscription_id=subscription_id,
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
            updated_at=datetime.now(),
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

        logger.info(
            f"Processing payment {provider_payment_id}"
        )

        payment = self.get_by_provider_id(
            provider_payment_id
        )

        if payment is None:
            logger.warning(
                f"Payment not found {provider_payment_id}"
            )
            return None

        if payment.status == PaymentStatus.PAID.value:
            logger.info(
                f"Payment already processed {payment.id}"
            )
            return payment

        if payment.status in (
            PaymentStatus.FAILED.value,
            PaymentStatus.CANCELED.value,
            PaymentStatus.EXPIRED.value,
        ):
            logger.warning(
                f"Payment has invalid status: {payment.status}"
            )
            return payment

        # ВАЖНО:
        # запоминаем тип операции ДО изменения payment.subscription_id
        is_renewal = payment.subscription_id is not None

        logger.info(
            f"Mark payment paid {payment.id}"
        )

        payment_repo.mark_paid(
            payment.id
        )

        payment_repo.cancel_other_pending(
            user_id=payment.user_id,
            except_payment_id=payment.id,
        )

        payment = self.get_payment(
            payment.id
        )

        if payment is None:
            logger.error(
                f"Payment disappeared after mark_paid: {provider_payment_id}"
            )
            return None

        # =========================================================
        # ПРОДЛЕНИЕ СУЩЕСТВУЮЩЕЙ ПОДПИСКИ
        # =========================================================

        if is_renewal:

            logger.info(
                f"Extending subscription {payment.subscription_id}"
            )

            old_subscription = (
                subscription_service.get_by_id(
                    payment.subscription_id
                )
            )

            if old_subscription is None:
                logger.error(
                    f"Subscription not found {payment.subscription_id}"
                )
                return payment

            old_expires_at = old_subscription.expires_at

            subscription = await vpn_service.extend(
                payment.subscription_id,
                payment.subscription_days,
            )

            logger.info(
                f"Subscription extended: "
                f"id={subscription.id}"
            )

        # =========================================================
        # НОВАЯ ПОДПИСКА
        # =========================================================

        else:

            logger.info(
                "Creating new VPN subscription..."
            )

            subscription = await vpn_service.purchase(
                user_id=payment.user_id,
                protocol=payment.protocol,
                days=payment.subscription_days,
            )

            # Привязываем созданную подписку к платежу
            payment_repo.set_subscription(
                payment.id,
                subscription.id,
            )

            logger.info(
                f"New subscription linked to payment: "
                f"payment={payment.id} "
                f"subscription={subscription.id}"
            )

        logger.info(
            f"Subscription ready {subscription.id}"
        )

        # =========================================================
        # TELEGRAM
        # =========================================================

        # Lazy import:
        # не тянем Telegram Bot слой во время импорта Backend API.
        from app.bot.services.telegram_service import telegram_service

        user = users_repo.get_by_id(
            payment.user_id
        )

        if user:

            if is_renewal:

                logger.info(
                    "Sending subscription renewal notification..."
                )

                await telegram_service.send_renew_notification(
                    user.telegram_id,
                    old_date=(
                        old_expires_at.strftime(
                            "%d.%m.%Y %H:%M"
                        )
                    ),
                    new_date=(
                        subscription.expires_at.strftime(
                            "%d.%m.%Y %H:%M"
                        )
                    ),
                )

            else:

                logger.info(
                    "Sending new subscription..."
                )

                await telegram_service.send_subscription(
                    user.telegram_id,
                    subscription,
                )

        logger.success(
            "Telegram message sent successfully"
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


        return True



    def expire_pending_payments(
        self,
    ):


        logger.info(
            "Expiring old pending payments..."
        )


        payment_repo.expire_old_pending(
            hours=24
        )


        logger.info(
            "Pending payments check finished."
        )

    async def create_payment_by_telegram(
        self,
        telegram_id: int,
        protocol: str,
        days: int,
        subscription_id: int | None = None,
    ):

        user = users_repo.get_by_telegram(
            telegram_id
        )

        if user is None:
            return None

        return self.create_payment(
            user_id=user.id,
            protocol=protocol,
            days=days,
            subscription_id=subscription_id,
        )


    def get_user_payments(
        self,
        user_id: int,
    ):

        return payment_repo.get_by_user_id(
            user_id
        )

payment_service = PaymentService()
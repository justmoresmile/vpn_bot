from datetime import datetime

from loguru import logger

from app.domain.payment import Payment
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.subscription_status import SubscriptionStatus

from app.repositories.payment_repository import payment_repo
from app.repositories.wallet_repository import wallet_repo
from app.payments.yookassa_client import yookassa_client
from app.services.vpn_service import vpn_service
from app.services.subscription_service import subscription_service
import asyncio


class PaymentProviderError(Exception):
    """Ошибка внешнего платёжного провайдера."""
    pass


class PaymentService:


    async def create_balance_topup(
        self,
        user_id: int,
        amount_rubles: int,
    ) -> Payment:

        if amount_rubles < 10:
            raise ValueError(
                "Minimum topup is 10 RUB"
            )

        if amount_rubles > 10000:
            raise ValueError(
                "Maximum topup is 10000 RUB"
            )

        amount_kopecks = (
            amount_rubles * 100
        )

        try:

            payment = await asyncio.to_thread(
                yookassa_client.create_payment,
                amount=amount_rubles,
                description=(
                    f"Пополнение баланса JustVPN "
                    f"на {amount_rubles} руб."
                ),
            )

        except Exception as exc:

            logger.exception(
                "YooKassa topup creation failed "
                "user={} amount={}",
                user_id,
                amount_rubles,
            )

            raise PaymentProviderError(
                "Payment provider is temporarily unavailable"
            ) from exc

        entity = Payment(
            id=None,
            user_id=user_id,
            subscription_id=None,
            protocol="balance",
            subscription_days=0,
            amount=float(amount_rubles),
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
            payment_type="balance_topup",
            amount_kopecks=amount_kopecks,
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



    async def activate_balance_access(
        self,
        user_id: int,
    ):
        from app.services.billing_service import (
            billing_service,
        )

        subscriptions = (
            subscription_service.get_by_user(
                user_id
            )
        )

        # Уже есть balance-подписка.
        # Новую никогда не создаём поверх существующей,
        # даже если автобиллинг отключён администратором.
        for subscription in subscriptions:
            if (
                subscription.billing_mode == "balance"
                and subscription.status
                != SubscriptionStatus.DELETED
            ):

                if not subscription.billing_enabled:

                    logger.info(
                        "Skip balance activation "
                        "user={} reason=billing_disabled "
                        "subscription={}",
                        user_id,
                        subscription.id,
                    )

                    return {
                        "status": "billing_disabled",
                        "subscription_id": (
                            subscription.id
                        ),
                    }

                result = await billing_service.process_subscription(
                    subscription.id
                )

                if (
                    result.get("status")
                    == "already_paid"
                ):
                    await billing_service.refresh_balance_expiry(
                        subscription.id
                    )

                return result

        # Если существует действующая fixed-подписка,
        # не начинаем списывать баланс параллельно.
        now = datetime.now()

        for subscription in subscriptions:
            if (
                subscription.billing_mode == "fixed"
                and subscription.status
                == SubscriptionStatus.ACTIVE
                and subscription.expires_at
                and subscription.expires_at > now
            ):
                logger.info(
                    "Skip balance subscription creation "
                    "user={} reason=active_fixed_subscription "
                    "subscription={}",
                    user_id,
                    subscription.id,
                )

                return {
                    "status": "active_fixed_subscription",
                    "subscription_id": subscription.id,
                }

        # Новый пользователь:
        # создаём balance-подписку сразу без
        # бесплатного технического периода.
        subscription = (
            await vpn_service
            .create_balance_subscription(
                user_id=user_id,
                protocol="vless",
            )
        )

        return await billing_service.process_subscription(
            subscription.id
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

        # Никогда не доверяем только входящему webhook.
        # Подтверждаем состояние платежа непосредственно
        # через API YooKassa.
        if payment.provider == "yookassa":

            provider_payment = await asyncio.to_thread(
                yookassa_client.get_payment,
                provider_payment_id,
            )

            if provider_payment.status != "succeeded":
                logger.warning(
                    "YooKassa payment is not succeeded "
                    "payment={} status={}",
                    payment.id,
                    provider_payment.status,
                )
                return payment

            provider_currency = (
                provider_payment.amount.currency
            )

            provider_amount = (
                float(
                    provider_payment.amount.value
                )
            )

            if (
                provider_currency != payment.currency
                or abs(
                    provider_amount
                    - float(payment.amount)
                ) > 0.001
            ):
                logger.error(
                    "YooKassa payment amount mismatch "
                    "payment={} expected={} {} "
                    "received={} {}",
                    payment.id,
                    payment.amount,
                    payment.currency,
                    provider_amount,
                    provider_currency,
                )
                raise RuntimeError(
                    "Payment amount verification failed"
                )

        if payment.status == PaymentStatus.PAID:

            logger.info(
                f"Payment already processed {payment.id}"
            )

            # Деньги второй раз не зачисляем.
            # Но для balance-платежа повторно проверяем
            # состояние доступа. Это позволяет восстановиться,
            # если YooKassa была обработана, а Remnawave
            # временно был недоступен.
            if payment.payment_type == "balance_topup":

                try:
                    result = await self.activate_balance_access(
                        payment.user_id
                    )

                    logger.info(
                        "Balance access retry "
                        "payment={} result={}",
                        payment.id,
                        result,
                    )

                except Exception:
                    logger.exception(
                        "Balance access retry failed "
                        "payment={}",
                        payment.id,
                    )
                    raise

            return payment

        if payment.status in (
            PaymentStatus.FAILED,
            PaymentStatus.CANCELED,
            PaymentStatus.EXPIRED,
        ):
            logger.warning(
                f"Payment has invalid status: {payment.status}"
            )
            return payment

        # =========================================================
        # BALANCE TOPUP
        # =========================================================

        if payment.payment_type == "balance_topup":

            payment, credited = (
                payment_repo.mark_paid_and_credit_wallet(
                    payment.id
                )
            )

            if payment is None:
                return None

            if credited:

                logger.success(
                    "Balance credited "
                    "payment={} user={} amount_kopecks={}",
                    payment.id,
                    payment.user_id,
                    payment.amount_kopecks,
                )

                activation_result = (
                    await self.activate_balance_access(
                        payment.user_id
                    )
                )

                logger.info(
                    "Balance access result "
                    "payment={} user={} result={}",
                    payment.id,
                    payment.user_id,
                    activation_result,
                )

                # =============================================
                # USER NOTIFICATION
                # =============================================

                try:
                    from app.services.user_notification_service import (
                        user_notification_service,
                    )

                    amount_rubles = (
                        int(payment.amount_kopecks or 0)
                        / 100
                    )

                    balance_rubles = (
                        int(
                            wallet_repo.get_balance(
                                payment.user_id
                            )
                            or 0
                        )
                        / 100
                    )

                    await user_notification_service.send_once(
                        user_id=payment.user_id,
                        event_key=(
                            f"balance_topup:"
                            f"payment:{payment.id}"
                        ),
                        notification_type="balance_topup",
                        title="💳 Баланс пополнен",
                        message=(
                            "На баланс JustVPN зачислено "
                            f"{amount_rubles:g} ₽.\n\n"
                            f"Текущий баланс: "
                            f"{balance_rubles:g} ₽.\n\n"
                            "VPN-доступ обновлён автоматически."
                        ),
                        related_type="payment",
                        related_id=payment.id,
                    )

                except Exception:
                    logger.exception(
                        "Balance topup notification failed "
                        "payment={} user={}",
                        payment.id,
                        payment.user_id,
                    )

            else:

                logger.info(
                    "Balance payment already credited "
                    "payment={}",
                    payment.id,
                )

            return payment


    async def check_payment(
        self,
        provider_payment_id: str,
    ) -> bool:


        payment = await asyncio.to_thread(
            yookassa_client.get_payment,
            provider_payment_id,
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

    def get_user_payments(
        self,
        user_id: int,
    ):

        return payment_repo.get_by_user_id(
            user_id
        )

payment_service = PaymentService()
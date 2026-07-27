from app.domain.user import User

from app.repositories.user_repository import users_repo
from app.repositories.subscription_repository import subscription_repo
from app.repositories.payment_repository import payment_repo

from app.domain.subscription import Subscription
from app.api.schemas.admin import AdminUserCardResponse
from app.domain.enums.payment_status import PaymentStatus

from app.services.vpn_service import vpn_service
from app.services.broadcast_service import BroadcastService

from app.bot.bot_instance import bot



class AdminService:


    def get_statistics(
        self,
    ) -> dict:

        return {

            "users": users_repo.count(),

            "subscriptions": subscription_repo.count(),

            "active_subscriptions":
                subscription_repo.count_active(),

            "expired_subscriptions":
                subscription_repo.count_expired(),

            "payments":
                payment_repo.count(),

            "paid_payments":
                payment_repo.count_paid(),

            "income":
                payment_repo.total_income(),

            "today_income":
                payment_repo.today_income(),

            "today_payments":
                payment_repo.today_paid(),

        }



    def get_users(
        self,
    ) -> list[User]:

        return users_repo.get_all()



    def search_users(
        self,
        query: str,
    ) -> list[User]:

        return users_repo.search(
            query
        )



    def filter_users(
        self,
        filter_type: str,
    ) -> list[User]:

        if filter_type == "active":

            return (
                users_repo
                .get_active_subscription_users()
            )


        if filter_type == "no_subscription":

            return (
                users_repo
                .get_without_subscription()
            )


        if filter_type == "expired":

            return (
                users_repo
                .get_expired_subscription_users()
            )


        if filter_type == "admins":

            return (
                users_repo
                .get_admins()
            )


        if filter_type == "all":

            return (
                users_repo
                .get_all()
            )


        raise ValueError(
            "Unknown filter type"
        )



    async def broadcast(
        self,
        target: str,
        message: str,
    ):

        service = BroadcastService(
            bot
        )

        return await service.broadcast(
            target,
            message,
        )



    def get_user(
        self,
        user_id: int,
    ) -> User | None:

        return users_repo.get_by_id(
            user_id
        )



    def get_user_card(
        self,
        user_id: int,
    ) -> AdminUserCardResponse | None:


        user = users_repo.get_by_id(
            user_id
        )


        if user is None:
            return None



        subscriptions = (
            subscription_repo
            .get_by_user(
                user_id
            )
        )


        payments = (
            payment_repo
            .get_by_user(
                user_id
            )
        )



        paid_payments = [

            payment

            for payment in payments

            if payment.status == PaymentStatus.PAID

        ]



        total_paid = sum(

            payment.amount

            for payment in paid_payments

        )



        return AdminUserCardResponse(

            id=user.id,

            telegram_id=user.telegram_id,

            username=user.username,

            first_name=user.first_name,

            created_at=user.created_at,

            is_admin=user.is_admin,

            subscriptions_count=len(
                subscriptions
            ),

            payments_count=len(
                paid_payments
            ),

            total_paid=total_paid,

        )



    def get_users_page(
        self,
        page: int = 1,
        limit: int = 10,
    ):


        users = users_repo.get_all()


        start = (
            page - 1
        ) * limit


        end = start + limit



        return {

            "users": users[start:end],

            "page": page,

            "total": len(users),

            "pages":
                (
                    (len(users) + limit - 1)
                    //
                    limit
                ),

        }



    def get_user_subscriptions(
        self,
        user_id: int,
    ) -> list[Subscription]:

        return (
            subscription_repo
            .get_by_user(
                user_id
            )
        )



    def get_user_payments(
        self,
        user_id: int,
    ):

        return (
            payment_repo
            .get_by_user(
                user_id
            )
        )



    async def renew_subscription(
        self,
        subscription_id: int,
        days: int,
    ) -> Subscription:

        return await vpn_service.renew(
            subscription_id,
            days,
        )



    async def disable_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None


        return await vpn_service.disable(
            subscription,
        )


    async def delete_subscription(
        self,
        subscription_id: int,
    ) -> None:

        await vpn_service.delete(
            subscription_id,
        )


    async def restore_subscription(
        self,
        subscription_id: int,
    ) -> Subscription | None:

        subscription = (
            subscription_repo.get_by_id(
                subscription_id
            )
        )

        if subscription is None:
            return None

        return await vpn_service.restore_client(
            subscription
        )

    async def get_subscription_config(
        self,
        subscription_id: int,
    ) -> str | None:


        return await vpn_service.get_config(
            subscription_id
        )



    async def get_subscription_file(
        self,
        subscription_id: int,
    ):


        subscription = (
            subscription_repo
            .get_by_id(
                subscription_id
            )
        )


        if subscription is None:

            return None



        return await vpn_service.get_file(
            subscription
        )


    async def get_payments_page(
        self,
        page: int = 1,
    ):

        limit = 10

        offset = (
            page - 1
        ) * limit


        payments = payment_repo.get_all(
            limit=limit,
            offset=offset,
        )


        total = payment_repo.count()


        pages = max(
            1,
            (total + limit - 1) // limit
        )


        return {
            "payments": [
                {
                    "id": payment.id,
                    "user_id": payment.user_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "status": payment.status.value,
                    "created_at": payment.created_at.strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                }
                for payment in payments
            ],
            "page": page,
            "pages": pages,
        }



    async def get_subscriptions_page(
        self,
        page: int = 1,
    ):

        limit = 10

        offset = (
            page - 1
        ) * limit


        subscriptions = subscription_repo.get_all(
            limit=limit,
            offset=offset,
        )


        total = subscription_repo.count()


        pages = max(
            1,
            (total + limit - 1) // limit
        )


        return {
            "subscriptions": [
                {
                    "id": sub.id,

                    "user_id": sub.user_id,

                    "client_email": sub.client_email,

                    "protocol": sub.protocol,

                    "status": sub.status.value,

                    "expires_at": sub.expires_at.strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                }
                for sub in subscriptions
            ],
            "page": page,
            "pages": pages,
        }

admin_service = AdminService()
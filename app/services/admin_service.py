from app.domain.user import User

from app.repositories.user_repository import users_repo
from app.repositories.subscription_repository import subscription_repo
from app.repositories.payment_repository import payment_repo

from app.domain.subscription import Subscription
from app.api.schemas.admin import AdminUserCardResponse
from app.domain.enums.payment_status import PaymentStatus

from app.services.vpn_service import vpn_service
from app.services.xui_client import XUIClient
from app.services.broadcast_service import BroadcastService

from app.bot.bot_instance import bot
from app.repositories.user_repository import users_repo
from app.repositories.subscription_repository import subscription_repo
from datetime import datetime
from app.repositories.server_repository import server_repo
from app.repositories.user_repository import users_repo
from app.domain.legacy_enums import SubscriptionStatus



class AdminService:

    def get_statistics(
        self,
    ) -> dict:

        return self.get_dashboard()




    def get_dashboard(
            self,
        ) -> dict:

          

        return {

            "users": users_repo.count(),

            "blocked_users": users_repo.count_blocked(),

            "admins": users_repo.count_admins(),

            "subscriptions": subscription_repo.count(),

            "active_subscriptions": subscription_repo.count_active(),

            "expired_subscriptions": subscription_repo.count_expired(),

            "payments": payment_repo.count(),

            "paid_payments": payment_repo.count_paid(),

            "income": payment_repo.total_income(),

            "today_income": payment_repo.today_income(),

            "today_payments": payment_repo.today_paid(),

            "servers": server_repo.count(),

            "online_servers": server_repo.count_online(),

        }


    

    def get_users(
        self,
    ) -> list[User]:

        return users_repo.get_all()



    def search_users(
    self,
        query: str,
    ):

        return users_repo.search(
            query
        )
    def has_active_subscription(
        self,
        user_id: int,
    ) -> bool:

        subscription = (
            subscription_repo
            .get_active_by_user(
                user_id
            )
        )

        return subscription is not None



    def has_expired_subscription(
        self,
        user_id: int,
    ) -> bool:

        subscriptions = (
            subscription_repo
            .get_by_user(
                user_id
            )
        )

        return any(
            s.status.value == "expired"
            for s in subscriptions
        )



    def has_any_subscription(
        self,
        user_id: int,
    ) -> bool:

        subscriptions = (
            subscription_repo
            .get_by_user(
                user_id
            )
        )

        return len(subscriptions) > 0

    def filter_users(
        self,
        type: str
    ):

        users = self.get_users()


        if type == "active":

            users = [
                user
                for user in users
                if self.has_active_subscription(user.id)
            ]


        elif type == "expired":

            users = [
                user
                for user in users
                if self.has_expired_subscription(user.id)
            ]


        elif type == "no_subscription":

            users = [
                user
                for user in users
                if not self.has_any_subscription(user.id)
            ]


        elif type == "admins":

            users = [
                user
                for user in users
                if user.is_admin
            ]


        elif type == "blocked":

            users = [
                user
                for user in users
                if user.is_blocked
            ]


        return users


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



        last_payment = None


        if paid_payments:

            payment = sorted(
                paid_payments,
                key=lambda x: (
                    x.paid_at
                    or x.created_at
                ),
                reverse=True,
            )[0]


            last_payment = {

                "amount": payment.amount,

                "paid_at": (
                    payment.paid_at
                    or payment.created_at
                ),

            }




        active_subscriptions = [

            s

            for s in subscriptions

            if s.status.value == "active"

        ]



        current_subscription = None

        days_left = None

        vpn = None



        if active_subscriptions:


            sub = active_subscriptions[0]



            current_subscription = {

                "id": sub.id,

                "protocol": sub.protocol,

                "status": sub.status.value,

                "expires_at": sub.expires_at,

                "client_email": sub.client_email,

            }



            if sub.expires_at:


                delta = (

                    sub.expires_at

                    - datetime.now()

                )


                days_left = max(

                    0,

                    delta.days

                )



            server = server_repo.get_by_id(

                sub.server_id

            )



            vpn = {

                "protocol": sub.protocol,

                "client_id": sub.client_id,

                "server": (

                    server.name

                    if server

                    else None

                ),

                "country": (

                    server.country

                    if server

                    else None

                ),

            }




        expired_subscriptions = [

            s

            for s in subscriptions

            if s.status.value == "expired"

        ]



        disabled_subscriptions = [

            s

            for s in subscriptions

            if s.status.value == "disabled"

        ]

        subscriptions_data = [

            {
                "id": sub.id,
                "protocol": sub.protocol,
                "status": sub.status.value,
                "expires_at": sub.expires_at,
                "client_email": sub.client_email,
            }

            for sub in subscriptions

        ]


        return AdminUserCardResponse(


            id=user.id,


            telegram_id=user.telegram_id,


            username=user.username,


            first_name=user.first_name,


            created_at=user.created_at,


            is_admin=user.is_admin,

            subscriptions=subscriptions_data,

            subscriptions_count=len(subscriptions),


            active_subscriptions=len(active_subscriptions),


            expired_subscriptions=len(expired_subscriptions),


            disabled_subscriptions=len(disabled_subscriptions),



            payments_count=len(paid_payments),


            total_paid=total_paid,



            current_subscription=current_subscription,


            last_payment=last_payment,


            days_left=days_left,


            vpn=vpn,

            

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


        result = []


        for user in users[start:end]:


            subscriptions = (
                subscription_repo
                .get_by_user(
                    user.id
                )
            )


            status = "none"


            for sub in subscriptions:

                if sub.status.value == "active":

                    status = "active"
                    break


                if sub.status.value == "disabled":

                    status = "disabled"


                if sub.status.value == "expired":

                    status = "expired"



            result.append(
                {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "status": status,
                }
            )



        return {

            "users": result,

            "page": page,

            "total": len(users),

            "pages":
                (
                    (len(users)+limit-1)
                    //
                    limit
                ),

        }

    def build_users_response(
        self,
        users,
    ):

        result = []


        for user in users:


            subscriptions = self.get_user_subscriptions(
                user.id
            )


            subscription_status = "none"


            if subscriptions:

                statuses = [
                    s.status.value
                    for s in subscriptions
                ]


                if "active" in statuses:

                    subscription_status = "active"

                elif "disabled" in statuses:

                    subscription_status = "disabled"

                elif "expired" in statuses:

                    subscription_status = "expired"


            payments = self.get_user_payments(
                user.id
            )


            total_paid = sum(

                p.amount

                for p in payments

                if p.status.value == "paid"

            )


            result.append(

                    {

                        "id": user.id,

                        "telegram_id": user.telegram_id,

                        "username": user.username,

                        "first_name": user.first_name,

                        "is_admin": user.is_admin,

                        "is_blocked": user.is_blocked,

                        "subscription_status": subscription_status,

                        "subscriptions_count": len(subscriptions),

                        "total_paid": total_paid,


                    }

                )


        return result

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

        await vpn_service.disable_subscription(
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


        payments = payment_repo.get_admin_payments(
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
                    "id": payment["id"],
                    "user_id": payment["user_id"], 

                    "telegram_id": payment["telegram_id"],

                    "username": payment["username"],

                    "first_name": payment["first_name"],


                    "subscription_id": payment["subscription_id"],


                    "client_email": payment["client_email"],


                    "protocol": payment["protocol"],


                    "subscription_days": payment["subscription_days"],


                    "amount": payment["amount"],


                    "currency": payment["currency"],


                    "status": payment["status"],


                    "provider": payment["provider"],


                    "created_at": datetime.fromtimestamp(
                        payment["created_at"]
                    ),


                    "paid_at": (
                        datetime.fromtimestamp(
                            payment["paid_at"]
                        )
                        if payment["paid_at"]
                        else None
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
        limit: int = 10,
    ):

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

            "total": total,

        }


    def get_subscription(
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


        user = users_repo.get_by_id(
            subscription.user_id
        )

        server = (
            server_repo.get_by_id(
                subscription.server_id
            )
        )


        days_left = None

        if subscription.expires_at:

            days_left = max(
                0,
                (
                    subscription.expires_at
                    - datetime.now()
                ).days
            )


        return {

        "id": subscription.id,

        "user_id": subscription.user_id,


        "user": {

            "id": user.id if user else None,

            "telegram_id": (
                user.telegram_id
                if user
                else None
            ),

            "username": (
                user.username
                if user
                else None
            ),

            "first_name": (
                user.first_name
                if user
                else None
            ),

        },

        "client_email": subscription.client_email,

        "client_id": subscription.client_id,

        "protocol": subscription.protocol,

        "status": subscription.status.value,

        "created_at": (
            subscription.created_at.isoformat()
            if subscription.created_at
            else None
        ),

        "expires_at": (
            subscription.expires_at.isoformat()
            if subscription.expires_at
            else None
        ),

        "days_left": days_left,

        "server": (
            server.name
            if server
            else None
        ),

        "country": (
            server.country
            if server
            else None
        ),

    }


    async def check_server(
        self,
        server_id: int,
    ):

        server = (
            server_repo
            .get_by_id(
                server_id
            )
        )


        if server is None:

            return None



        try:

            async with XUIClient(
                server
            ) as xui:


                inbounds = await xui.get_inbounds()



            return {

                "server_id": server.id,

                "status": "online",

                "inbounds": len(inbounds),

                "message": "XUI connection OK",

            }



        except Exception as e:


            return {

                "server_id": server.id,

                "status": "offline",

                "message": str(e),

            }


    async def create_subscription(
            self,
            user_id: int,
            days: int,
            protocol: str = "wireguard",
        ):

            return await vpn_service.create(
                user_id=user_id,
                protocol=protocol,
                days=days,
            )


    async def get_server_stats(
        self,
        server_id: int,
    ):

        server = (
            server_repo
            .get_by_id(
                server_id
            )
        )


        if server is None:
            return None



        subscriptions = (
            subscription_repo
            .get_by_server(
                server_id
            )
        )


        active = 0
        disabled = 0
        expired = 0


        for sub in subscriptions:


            if sub.status.value == "active":

                active += 1


            elif sub.status.value == "disabled":

                disabled += 1


            elif sub.status.value == "expired":

                expired += 1



        return {

            "server_id": server.id,

            "server": server.name,

            "clients": len(subscriptions),

            "active_clients": active,

            "disabled_clients": disabled,

            "expired_clients": expired,

        }

    async def block_user(
        self,
        user_id: int,
    ):

        user = users_repo.get_by_id(
            user_id
        )

        if user is None:
            return None


        # блокируем пользователя
        users_repo.block(
            user_id
        )


        # отключаем все его подписки
        subscriptions = (
            subscription_repo
            .get_by_user(
                user_id
            )
        )


        for subscription in subscriptions:

            if subscription.status == SubscriptionStatus.ACTIVE:

                await self.disable_subscription(
                    subscription.id
                )


        return users_repo.get_by_id(
            user_id
        )


    async def unblock_user(
        self,
        user_id: int,
    ):

        user = users_repo.get_by_id(
            user_id
        )

        if user is None:
            return None


        users_repo.unblock(
            user_id
        )


        return users_repo.get_by_id(
            user_id
        )

    def get_users_statistics(
        self,
    ):

        users = users_repo.get_all()


        active = 0
        expired = 0
        none = 0
        admins = 0


        for user in users:

            if user.is_admin:
                admins += 1


            subscriptions = (
                subscription_repo
                .get_by_user(
                    user.id
                )
            )


            if not subscriptions:

                none += 1

                continue



            statuses = [
                s.status.value
                for s in subscriptions
            ]


            if "active" in statuses:

                active += 1

            elif "expired" in statuses:

                expired += 1



        return {

            "total": len(users),

            "active": active,

            "expired": expired,

            "none": none,

            "admins": admins,

        }


admin_service = AdminService()
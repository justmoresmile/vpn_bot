from aiogram import Bot

from app.repositories.user_repository import users_repo


class BroadcastService:


    def __init__(
        self,
        bot: Bot,
    ):
        self.bot = bot


    async def send_to_users(
        self,
        users,
        message: str,
    ):

        sent = 0
        failed = 0

        for user in users:

            try:

                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                )

                sent += 1


            except Exception:

                failed += 1


        return {
            "sent": sent,
            "failed": failed,
        }



    async def broadcast(
        self,
        target: str,
        message: str,
    ):

        if target == "all":

            users = users_repo.get_all()


        elif target == "active":

            users = (
                users_repo
                .get_active_subscription_users()
            )


        elif target == "no_subscription":

            users = (
                users_repo
                .get_without_subscription()
            )


        elif target == "admins":

            users = (
                users_repo
                .get_admins()
            )


        else:

            raise ValueError(
                "Unknown broadcast target"
            )


        return await self.send_to_users(
            users,
            message,
        )
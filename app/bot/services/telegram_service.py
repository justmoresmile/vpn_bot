from aiogram.enums import ParseMode

from app.bot.bot_instance import bot
from app.logger import logger
from app.services.vpn_service import vpn_service


class TelegramService:

    async def send_subscription(
        self,
        user_id: int,
        subscription,
    ) -> None:

        try:

            if subscription.protocol == "wireguard":

                config = await vpn_service.get_wireguard_config(
                    subscription
                )

            else:

                config = await vpn_service.get_config(
                    subscription.id
                )

            text = (
                "✅ <b>Оплата успешно получена!</b>\n\n"
                "🔐 Ваш VPN готов.\n\n"
                "<b>Конфигурация:</b>\n"
                f"<code>{config}</code>"
            )

            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML,
            )

        except Exception:
            logger.exception(
                "Не удалось отправить VPN пользователю %s",
                user_id,
            )
            raise


telegram_service = TelegramService()
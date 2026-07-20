from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile

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

            filename, data = await vpn_service.get_file(
                subscription
            )

            file = BufferedInputFile(
                data,
                filename=filename,
            )

            await bot.send_message(
                chat_id=user_id,
                text=(
                    "✅ <b>Оплата успешно получена!</b>\n\n"
                    "🔐 Ваш VPN готов.\n\n"
                    "📁 Конфигурационный файл отправлен ниже."
                ),
                parse_mode=ParseMode.HTML,
            )

            await bot.send_document(
                chat_id=user_id,
                document=file,
                caption="📥 WireGuard конфигурация",
            )

        except Exception:

            logger.exception(
                "Не удалось отправить VPN пользователю %s",
                user_id,
            )

            raise


telegram_service = TelegramService()
from aiogram import Router, F
from aiogram.types import Message

from app.bot.clients.api_client import api_client


router = Router()


@router.message(F.text == "🔑 API Key")
async def api_key(
    message: Message,
):

    try:

        result = await api_client.get_api_key(
            telegram_id=message.from_user.id
        )

    except Exception:

        await message.answer(
            "Не удалось получить API Key."
        )

        return


    await message.answer(
        f"<b>Ваш API Key</b>\n\n"
        f"<code>{result['api_key']}</code>\n\n"
        "⚠️ Никому его не сообщайте.",
        parse_mode="HTML",
    )
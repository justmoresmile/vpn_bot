from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)

from app.bot.handlers.start import router as start_router
from app.bot.handlers.subscriptions import router as subscriptions_router
from app.bot.handlers.buy import router as buy_router
from app.bot.handlers.subscription_actions import (
    router as subscription_actions_router,
)
from app.bot.handlers.instruction import router as instruction_router
from app.bot.handlers.support import router as support_router
from app.bot.handlers.account import router as account_router
from app.bot.handlers.admin import router as admin_router

from app.ui.screens.admin import (
    admin_subscriptions_screen,
    admin_subscription_screen,
)
from app.bot.keyboards.admin import (
    admin_subscriptions_keyboard,
)

from app.bot.clients.api_client import api_client



from app.bot.keyboards.admin import (
    admin_subscription_menu,
)

router = Router()

router.include_router(start_router)
router.include_router(subscriptions_router)
router.include_router(buy_router)
router.include_router(subscription_actions_router)
router.include_router(instruction_router)
router.include_router(support_router)
router.include_router(account_router)
router.include_router(admin_router)


@router.callback_query(
    F.data == "admin_user_subscriptions_back"
)
async def admin_user_subscriptions_back(
    callback: CallbackQuery,
):

    data = await api_client.get_admin_subscriptions(
        callback.from_user.id,
    )


    await callback.message.edit_text(
        admin_subscriptions_screen(
            data["subscriptions"]
        ),
        parse_mode="HTML",
        reply_markup=admin_subscriptions_keyboard(
            data["subscriptions"]
        ),
    )


    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "admin_subscription:"
    )
)
async def admin_subscription(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )


    data = await api_client.get_admin_subscription(
        callback.from_user.id,
        subscription_id,
    )


    print(data)


    await callback.message.edit_text(
        admin_subscription_screen(
            data
        ),
        reply_markup=admin_subscription_menu(
            subscription_id,
            data["user_id"],
        ),
    )


    await callback.answer()



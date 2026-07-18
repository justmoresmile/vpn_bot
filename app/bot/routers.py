
from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.profile import router as profile_router
from app.bot.handlers.subscriptions import router as subscriptions_router
from app.bot.handlers.buy import router as buy_router
from app.bot.handlers.subscription_actions import (
    router as subscription_actions_router,
)
router = Router()

router.include_router(start_router)
router.include_router(profile_router)
router.include_router(subscriptions_router)
router.include_router(buy_router)
router.include_router(subscription_actions_router)


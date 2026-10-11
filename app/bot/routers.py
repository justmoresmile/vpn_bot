from aiogram import Router

from app.bot.handlers.start import (
    router as start_router,
)
from app.bot.handlers.support import (
    router as support_router,
)


router = Router()

router.include_router(start_router)
router.include_router(support_router)

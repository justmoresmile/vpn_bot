
from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.user import router as user_router
from app.api.routes.subscription import router as subscription_router
from app.api.routes.vpn import router as vpn_router
from app.api.routes.payment import router as payment_router
from app.api.routes.trial import router as trial_router
from app.api.routes.support import router as support_router
from app.api.routes.notification import router as notification_router


router = APIRouter(
    prefix="/api/v1",
)


router.include_router(
    health_router
)

router.include_router(
    auth_router
)

router.include_router(
    user_router
)

router.include_router(
    subscription_router
)

router.include_router(
    vpn_router
)

router.include_router(
    payment_router
)

router.include_router(
    trial_router
)

router.include_router(
    support_router
)

router.include_router(
    notification_router
)




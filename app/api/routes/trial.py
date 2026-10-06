from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.api.dependencies.auth import (
    get_current_user,
)
from app.domain.user import User
from app.repositories.subscription_repository import (
    subscription_repo,
)
from app.repositories.user_repository import (
    users_repo,
)
from app.services.trial_service import (
    trial_service,
)


router = APIRouter(
    prefix="/trial",
    tags=["Trial"],
)


@router.get(
    "/status"
)
async def get_trial_status(
    user: User = Depends(
        get_current_user
    ),
):
    current = users_repo.get_by_id(
        user.id
    )

    if current is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    subscriptions = (
        subscription_repo.get_by_user(
            user.id
        )
    )

    now = datetime.now()

    active = (
        current.trial_used
        and current.trial_ends_at is not None
        and current.trial_ends_at > now
    )

    remaining_seconds = 0

    if active:
        remaining_seconds = max(
            0,
            int(
                (
                    current.trial_ends_at
                    - now
                ).total_seconds()
            ),
        )

    available = (
        not current.trial_used
        and len(subscriptions) == 0
    )

    return {
        "available": available,
        "used": current.trial_used,
        "active": active,
        "started_at": (
            current.trial_started_at.isoformat()
            if current.trial_started_at
            else None
        ),
        "ends_at": (
            current.trial_ends_at.isoformat()
            if current.trial_ends_at
            else None
        ),
        "remaining_seconds": (
            remaining_seconds
        ),
        "duration_days": 3,
    }


@router.post(
    "/start"
)
async def start_trial(
    user: User = Depends(
        get_current_user
    ),
):
    try:
        return await trial_service.start(
            user.id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.post(
    "/finish"
)
async def finish_trial(
    device_limit: int,
    user: User = Depends(
        get_current_user
    ),
):
    try:

        return await trial_service.finish(
            user.id,
            device_limit=device_limit,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

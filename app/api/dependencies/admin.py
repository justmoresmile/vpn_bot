from fastapi import Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.domain.user import User


async def get_current_admin(
    user: User = Depends(
        get_current_user
    ),
) -> User:

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return user
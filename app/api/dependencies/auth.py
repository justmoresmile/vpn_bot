from fastapi import (
    HTTPException,
    Security,
    Depends,
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from app.repositories.user_repository import users_repo
from app.domain.user import User
from app.services.auth.jwt_service import jwt_service


security = HTTPBearer()



async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> User:

    token = credentials.credentials

    user_id = jwt_service.get_user_id(
        token
    )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


    user = users_repo.get_by_id(
        user_id
    )


    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    return user




async def get_current_admin(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:

    if not current_user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )


    return current_user
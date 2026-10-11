from fastapi import (
    APIRouter,
    Depends,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.domain.user import User

from app.repositories.notification_repository import (
    notification_repo,
)

from app.api.schemas.notification import (
    NotificationResponse,
    NotificationUnreadResponse,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
async def get_notifications(
    user: User = Depends(
        get_current_user
    ),
):

    rows = (
        notification_repo.get_user_notifications(
            user.id
        )
    )

    return [
        NotificationResponse(
            id=row["id"],
            type=row["type"],
            title=row["title"],
            message=row["message"],
            related_type=row["related_type"],
            related_id=row["related_id"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.get(
    "/unread-count",
    response_model=NotificationUnreadResponse,
)
async def get_unread_count(
    user: User = Depends(
        get_current_user
    ),
):

    return NotificationUnreadResponse(
        count=notification_repo.unread_count(
            user.id
        )
    )


@router.post(
    "/{notification_id}/read",
)
async def mark_notification_read(
    notification_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    notification_repo.mark_read(
        user_id=user.id,
        notification_id=notification_id,
    )

    return {
        "success": True,
    }


@router.post(
    "/read-all",
)
async def mark_all_notifications_read(
    user: User = Depends(
        get_current_user
    ),
):

    notification_repo.mark_all_read(
        user.id
    )

    return {
        "success": True,
    }

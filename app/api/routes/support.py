from loguru import logger
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.api.dependencies.auth import (
    get_current_user,
)

from app.api.schemas.support import (
    SupportTicketCreateRequest,
    SupportMessageCreateRequest,
    SupportTicketResponse,
    SupportTicketDetailsResponse,
    SupportMessageResponse,
)

from app.domain.user import User

from app.services.support_service import (
    support_service,
)

from app.repositories.support_repository import (
    support_repo,
)

from app.bot.services.telegram_service import (
    telegram_service,
)


router = APIRouter(
    prefix="/support",
    tags=["Support"],
)


def ticket_to_response(
    ticket,
) -> SupportTicketResponse:

    return SupportTicketResponse(
        id=ticket.id,
        user_id=ticket.user_id,
        subject=ticket.subject,
        category=ticket.category,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
    )


def message_to_response(
    message,
) -> SupportMessageResponse:

    return SupportMessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        sender_type=message.sender_type,
        sender_id=message.sender_id,
        message=message.message,
        is_read=message.is_read,
        created_at=message.created_at,
    )


@router.get(
    "/tickets",
    response_model=list[
        SupportTicketResponse
    ],
)
async def get_tickets(
    user: User = Depends(
        get_current_user
    ),
):

    tickets = (
        support_service.get_user_tickets(
            user.id
        )
    )

    return [
        ticket_to_response(ticket)
        for ticket in tickets
    ]


@router.post(
    "/tickets",
    response_model=SupportTicketDetailsResponse,
)
async def create_ticket(
    request: SupportTicketCreateRequest,
    user: User = Depends(
        get_current_user
    ),
):

    try:

        ticket = (
            support_service.create_ticket(
                user_id=user.id,
                subject=request.subject,
                message=request.message,
                category=request.category,
            )
        )

        messages = (
            support_service.get_messages(
                user_id=user.id,
                ticket_id=ticket.id,
            )
        )

        thread_id = await telegram_service.create_support_topic(
            chat_id=-1004442060823,
            ticket_id=ticket.id,
            user_id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            subject=ticket.subject,
            message=messages[0].message,
        )

        support_repo.set_telegram_thread_id(
            ticket.id,
            thread_id,
        )

        return SupportTicketDetailsResponse(
            **ticket_to_response(
                ticket
            ).model_dump(),
            messages=[
                message_to_response(message)
                for message in messages
            ],
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/tickets/{ticket_id}",
    response_model=SupportTicketDetailsResponse,
)
async def get_ticket(
    ticket_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    try:

        ticket = (
            support_service.get_user_ticket(
                user_id=user.id,
                ticket_id=ticket_id,
            )
        )

        messages = (
            support_service.get_messages(
                user_id=user.id,
                ticket_id=ticket_id,
            )
        )

        return SupportTicketDetailsResponse(
            **ticket_to_response(
                ticket
            ).model_dump(),
            messages=[
                message_to_response(message)
                for message in messages
            ],
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.post(
    "/tickets/{ticket_id}/messages",
    response_model=SupportMessageResponse,
)
async def send_message(
    ticket_id: int,
    request: SupportMessageCreateRequest,
    user: User = Depends(
        get_current_user
    ),
):

    try:

        message = (
            support_service.add_user_message(
                user_id=user.id,
                ticket_id=ticket_id,
                message=request.message,
            )
        )

        ticket = support_repo.get_ticket(
            ticket_id
        )

        if (
            ticket
            and ticket.telegram_thread_id
        ):
            await telegram_service.send_support_topic_message(
                chat_id=-1004442060823,
                thread_id=ticket.telegram_thread_id,
                sender="user",
                message=message.message,
                username=user.username,
            )

        return message_to_response(
            message
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.post(
    "/tickets/{ticket_id}/close",
    response_model=SupportTicketResponse,
)
async def close_ticket(
    ticket_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    try:

        ticket = (
            support_service.close_ticket(
                user_id=user.id,
                ticket_id=ticket_id,
            )
        )

        return ticket_to_response(
            ticket
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


@router.delete(
    "/tickets/{ticket_id}",
)
async def delete_ticket(
    ticket_id: int,
    user: User = Depends(
        get_current_user
    ),
):

    try:

        ticket = (
            support_service.get_user_ticket(
                user_id=user.id,
                ticket_id=ticket_id,
            )
        )

        if ticket.telegram_thread_id:

            try:

                await telegram_service.delete_support_topic(
                    chat_id=-1004442060823,
                    thread_id=ticket.telegram_thread_id,
                )

            except Exception:
                logger.exception(
                    "Failed to delete support topic: "
                    "ticket=%s thread=%s",
                    ticket.id,
                    ticket.telegram_thread_id,
                )

        support_service.delete_user_ticket(
            user_id=user.id,
            ticket_id=ticket_id,
        )

        return {
            "success": True,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

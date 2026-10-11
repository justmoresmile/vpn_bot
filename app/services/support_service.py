from app.domain.support import (
    SupportTicket,
    SupportMessage,
)

from app.repositories.support_repository import (
    support_repo,
)

from app.repositories.notification_repository import (
    notification_repo,
)


class SupportService:

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def _clean_text(
        value: str,
        *,
        field_name: str,
        max_length: int,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} не может быть пустым"
            )

        if len(value) > max_length:
            raise ValueError(
                f"{field_name} слишком длинный"
            )

        return value

    # ==========================================================
    # TICKETS
    # ==========================================================

    def create_ticket(
        self,
        *,
        user_id: int,
        subject: str,
        message: str,
        category: str | None = None,
    ) -> SupportTicket:

        subject = self._clean_text(
            subject,
            field_name="Тема",
            max_length=120,
        )

        message = self._clean_text(
            message,
            field_name="Сообщение",
            max_length=4000,
        )

        if category is not None:
            category = category.strip() or None

        ticket = support_repo.create_ticket(
            user_id=user_id,
            subject=subject,
            category=category,
        )

        support_repo.create_message(
            ticket_id=ticket.id,
            sender_type="user",
            sender_id=user_id,
            message=message,
            is_read=False,
        )

        created = support_repo.get_ticket(
            ticket.id
        )

        if created is None:
            raise RuntimeError(
                "Support ticket disappeared after creation"
            )

        return created

    def get_user_tickets(
        self,
        user_id: int,
    ) -> list[SupportTicket]:

        return support_repo.get_user_tickets(
            user_id
        )

    def get_user_ticket(
        self,
        *,
        user_id: int,
        ticket_id: int,
    ) -> SupportTicket:

        ticket = support_repo.get_ticket(
            ticket_id
        )

        if ticket is None:
            raise ValueError(
                "Обращение не найдено"
            )

        if ticket.user_id != user_id:
            raise PermissionError(
                "Нет доступа к обращению"
            )

        return ticket

    def get_messages(
        self,
        *,
        user_id: int,
        ticket_id: int,
    ) -> list[SupportMessage]:

        self.get_user_ticket(
            user_id=user_id,
            ticket_id=ticket_id,
        )

        return support_repo.get_messages(
            ticket_id
        )

    # ==========================================================
    # USER MESSAGES
    # ==========================================================

    def add_user_message(
        self,
        *,
        user_id: int,
        ticket_id: int,
        message: str,
    ) -> SupportMessage:

        ticket = self.get_user_ticket(
            user_id=user_id,
            ticket_id=ticket_id,
        )

        if ticket.status == "closed":
            raise ValueError(
                "Обращение уже закрыто"
            )

        message = self._clean_text(
            message,
            field_name="Сообщение",
            max_length=4000,
        )

        created = support_repo.create_message(
            ticket_id=ticket_id,
            sender_type="user",
            sender_id=user_id,
            message=message,
            is_read=False,
        )

        support_repo.update_status(
            ticket_id,
            "open",
        )

        return created

    # ==========================================================
    # ADMIN
    # ==========================================================

    def get_ticket(
        self,
        ticket_id: int,
    ) -> SupportTicket:

        ticket = support_repo.get_ticket(
            ticket_id
        )

        if ticket is None:
            raise ValueError(
                "Обращение не найдено"
            )

        return ticket


    def get_ticket_messages(
        self,
        *,
        ticket_id: int,
    ) -> list[SupportMessage]:

        self.get_ticket(
            ticket_id
        )

        return support_repo.get_messages(
            ticket_id
        )


    def add_admin_message(
        self,
        *,
        admin_id: int,
        ticket_id: int,
        message: str,
    ) -> SupportMessage:

        ticket = self.get_ticket(
            ticket_id
        )

        if ticket.status == "closed":
            raise ValueError(
                "Обращение уже закрыто"
            )

        message = self._clean_text(
            message,
            field_name="Сообщение",
            max_length=4000,
        )

        created = support_repo.create_message(
            ticket_id=ticket_id,
            sender_type="admin",
            sender_id=admin_id,
            message=message,
            is_read=False,
        )

        support_repo.update_status(
            ticket_id,
            "waiting_user",
        )

        notification_repo.create(
            user_id=ticket.user_id,
            notification_type="support_reply",
            title="Ответ поддержки",
            message=message,
            related_type="support_ticket",
            related_id=ticket.id,
        )

        return created


    def close_ticket_admin(
        self,
        *,
        ticket_id: int,
    ) -> SupportTicket:

        ticket = self.get_ticket(
            ticket_id
        )

        if ticket.status != "closed":

            support_repo.update_status(
                ticket_id,
                "closed",
            )

        updated = support_repo.get_ticket(
            ticket_id
        )

        if updated is None:
            raise RuntimeError(
                "Failed to load closed support ticket"
            )

        return updated


    def delete_user_ticket(
        self,
        *,
        user_id: int,
        ticket_id: int,
    ) -> SupportTicket:

        ticket = self.get_user_ticket(
            user_id=user_id,
            ticket_id=ticket_id,
        )

        notification_repo.delete_by_related(
            user_id=user_id,
            related_type="support_ticket",
            related_id=ticket_id,
        )

        support_repo.delete_ticket(
            ticket_id
        )

        return ticket


    # ==========================================================
    # CLOSE
    # ==========================================================

    def close_ticket(
        self,
        *,
        user_id: int,
        ticket_id: int,
    ) -> SupportTicket:

        ticket = self.get_user_ticket(
            user_id=user_id,
            ticket_id=ticket_id,
        )

        if ticket.status != "closed":

            support_repo.update_status(
                ticket_id,
                "closed",
            )

        updated = support_repo.get_ticket(
            ticket_id
        )

        if updated is None:
            raise RuntimeError(
                "Failed to load closed support ticket"
            )

        return updated


support_service = SupportService()

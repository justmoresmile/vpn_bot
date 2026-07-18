from uuid import uuid4


def generate_client_email(user_id: int) -> str:
    """
    Генерирует уникальный email клиента для 3x-ui.
    """

    return f"user{user_id}-{uuid4().hex[:8]}"
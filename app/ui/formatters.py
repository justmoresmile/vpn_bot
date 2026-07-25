from datetime import datetime


def format_date(
    date: datetime,
) -> str:

    return date.strftime(
        "%d.%m.%Y"
    )


def format_days(
    days: int,
) -> str:

    if days == 1:
        return "1 день"

    if 2 <= days <= 4:
        return f"{days} дня"

    return f"{days} дней"


def format_status(
    active: bool,
) -> str:

    return (
        "🟢 Подписка активна"
        if active
        else "🔴 Подписка неактивна"
    )
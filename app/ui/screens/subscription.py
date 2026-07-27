def subscription_screen(
    subscription: dict,
) -> str:

    expires = subscription.get(
        "expires_at",
        "-"
    )

    protocol = subscription.get(
        "protocol",
        "-"
    ).title()

    status_value = subscription.get(
        "status",
        "-"
    )


    if status_value == "active":

        status = "🟢 Подписка активна"

    else:

        status = "🔴 Подписка неактивна"


    return (
        "<b>📡 Мой VPN</b>\n\n"
        f"🆔 ID: <code>{subscription.get('id')}</code>\n"
        f"🔌 Протокол: {protocol}\n"
        f"📌 Статус: {status}\n"
        f"📅 До: {expires}\n"
    )



def no_subscription_screen() -> str:

    return (
        "<b>📡 Подписок нет</b>\n\n"
        "У вас нет активной VPN подписки."
    )


def my_vpn_screen(
    subscription: dict,
    days_left: int,
) -> str:

    expires = subscription.get(
        "expires_at",
        "-"
    )

    if "T" in expires:
        expires = expires.split("T")[0]

        year, month, day = expires.split("-")
        expires = f"{day}.{month}.{year}"


    email = subscription.get(
        "client_email",
        "-"
    )


    return (
        "🔐 <b>Ваш JustVPN</b>\n\n"

        f"📧 <b>Профиль:</b>\n"
        f"<code>{email}</code>\n\n"

        f"📅 <b>Действует до:</b>\n"
        f"{expires}\n\n"

        f"⏳ <b>Осталось:</b>\n"
        f"{days_left} дней\n\n"

        "🚀 VPN работает.\n\n"

        "Спасибо что пользуетесь нашим сервисом ❤️"
    )

def subscription_renew_success_screen(
    old_date: str,
    new_date: str,
) -> str:

    return (
        "<b>✅ Подписка продлена</b>\n\n"
        "🔄 Ваш VPN продлён.\n\n"
        f"📅 Было до:\n"
        f"<b>{old_date}</b>\n\n"
        f"📅 Теперь действует до:\n"
        f"<b>{new_date}</b>\n\n"
        "Спасибо за использование JustVPN ❤️"
    )
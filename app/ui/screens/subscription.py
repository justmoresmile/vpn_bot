def subscription_screen(
    subscription,
    status=None,
) -> str:

    current_status = (
        status
        if status
        else subscription.status
    )

    subscription_status = (
        current_status.value
        if hasattr(current_status, "value")
        else current_status
    )

    return (
        "<b>📡 Подписка</b>\n\n"
        f"🆔 ID: <code>{subscription.id}</code>\n"
        f"🔌 Протокол: {subscription.protocol}\n"
        f"📌 Статус: {subscription_status}\n"
        f"📅 До: {subscription.expires_at}\n"
    )

def no_subscription_screen() -> str:

    return (
        "<b>📡 Подписок нет</b>\n\n"
        "У вас нет активной VPN подписки."
    )


def my_vpn_screen(
    subscription,
) -> str:

    return (
        "<b>🔐 Мой VPN</b>\n\n"
        f"🆔 ID: <code>{subscription.id}</code>\n"
        f"🔌 Протокол: {subscription.protocol}\n"
        f"📌 Статус: {subscription.status.value}\n"
        f"📅 До: {subscription.expires_at}\n"
    )


def subscription_renew_success_screen(
    old_date: str,
    new_date: str,
) -> str:

    return (
        "✅ <b>Подписка продлена</b>\n\n"

        "🔄 Ваш VPN продлён.\n\n"

        f"📅 Было до:\n"
        f"<b>{old_date}</b>\n\n"

        f"📅 Теперь действует до:\n"
        f"<b>{new_date}</b>\n\n"

        "Спасибо за использование JustVPN ❤️"
    )
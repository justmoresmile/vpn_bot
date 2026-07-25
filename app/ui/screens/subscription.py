def subscription_screen(
    subscription,
) -> str:

    return (
        "<b>📡 Подписка</b>\n\n"
        f"ID: <code>{subscription.id}</code>\n"
        f"Протокол: {subscription.protocol}\n"
        f"Статус: {subscription.status.value}\n"
        f"До: {subscription.expires_at}\n"
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
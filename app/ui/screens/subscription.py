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
) -> str:

    return subscription_screen(subscription)
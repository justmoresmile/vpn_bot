def admin_statistics_screen(
    stats: dict,
) -> str:

    return (
        "<b>📊 Статистика</b>\n\n"
        f"👤 Пользователей: {stats['users']}\n"
        f"📡 Подписок: {stats['subscriptions']}\n"
        f"🟢 Активных: {stats['active_subscriptions']}\n"
        f"🔴 Истекших: {stats['expired_subscriptions']}\n\n"
        f"💳 Платежей: {stats['payments']}\n"
        f"✅ Оплачено: {stats['paid_payments']}\n\n"
        f"💰 Доход: {stats['income']} ₽\n"
        f"📅 Сегодня: {stats['today_income']} ₽\n"
        f"🛒 Сегодня оплат: {stats['today_payments']}"
    )



def admin_users_page_screen(
    data: dict,
) -> str:

    users = data.get(
        "users",
        [],
    )

    text = (
        "<b>👥 Пользователи</b>\n\n"
    )

    if not users:

        return (
            text +
            "Пользователей нет."
        )


    for user in users:

        username = (
            f"@{user['username']}"
            if user.get("username")
            else "-"
        )


        text += (
            f"🆔 <code>{user['id']}</code>\n"
            f"👤 {username}\n"
            f"📱 {user['telegram_id']}\n"
            "────────────\n"
        )


    text += (
        f"\nСтраница "
        f"{data['page']}/{data['pages']}"
    )

    return text



def admin_user_screen(
    user: dict,
) -> str:

    username = (
        f"@{user['username']}"
        if user.get("username")
        else "-"
    )

    first_name = (
        user["first_name"]
        if user.get("first_name")
        else "-"
    )


    return (
        "<b>👤 Пользователь</b>\n\n"
        f"🆔 ID: <code>{user['id']}</code>\n"
        f"📱 Telegram: <code>{user['telegram_id']}</code>\n"
        f"👤 Username: {username}\n"
        f"🏷 Имя: {first_name}\n\n"
        f"👑 Администратор: "
        f"{'Да' if user['is_admin'] else 'Нет'}"
    )


def admin_payments_screen(
    data: dict,
) -> str:

    payments = data.get(
        "payments",
        [],
    )

    text = (
        "<b>💳 Платежи</b>\n\n"
    )


    if not payments:

        return (
            text +
            "Платежей нет."
        )


    for payment in payments:

        text += (
            f"🆔 ID: <code>{payment['id']}</code>\n"
            f"👤 User: {payment['user_id']}\n"
            f"💰 Сумма: {payment['amount']} ₽\n"
            f"📌 Статус: {payment['status']}\n"
            f"📅 {payment['created_at']}\n"
            "────────────\n"
        )


    text += (
        f"\nСтраница {data['page']}/{data['pages']}"
    )


    return text


def admin_subscriptions_screen(
        data: dict,
    ) -> str:

        subscriptions = data.get(
            "subscriptions",
            [],
        )

        text = (
            "<b>📡 Подписки</b>\n\n"
        )


        if not subscriptions:

            return (
                text +
                "Подписок нет."
            )


        for sub in subscriptions:

            text += (
                f"🆔 ID: <code>{sub['id']}</code>\n"
                f"👤 User: {sub['user_id']}\n"
                f"🔌 Протокол: {sub['protocol']}\n"
                f"📌 Статус: {sub['status']}\n"
                f"📅 До: {sub['expires_at']}\n"
                "────────────\n"
            )


        text += (
            f"\nСтраница {data['page']}/{data['pages']}"
        )


        return text


def admin_subscriptions_screen(
    subscriptions: list,
) -> str:


    text = (
        "📡 <b>Подписки</b>\n\n"
    )


    if not subscriptions:

        return (
            text +
            "Подписок нет."
        )


    for sub in subscriptions:

        text += (
            f"🆔 ID: <code>{sub['id']}</code>\n"
            f"👤 User: {sub['user_id']}\n"
            f"🔌 Протокол: {sub['protocol']}\n"
            f"📌 Статус: {sub['status']}\n"
            f"📅 До: {sub['expires_at']}\n"
            "────────────\n"
        )


    return text


def admin_subscription_screen(
    sub: dict,
):

    return (
        "📡 <b>Подписка</b>\n\n"
        f"🆔 ID: <code>{sub['id']}</code>\n"
        f"👤 User: {sub['user_id']}\n"
        f"🔌 Протокол: {sub['protocol']}\n"
        f"📌 Статус: {sub['status']}\n"
        f"📅 До: {sub['expires_at']}"
    )
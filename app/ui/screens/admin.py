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

            "👤 <b>Клиент</b>\n\n"

            f"🆔 ID:\n"
            f"<code>{user['id']}</code>\n\n"

            f"📱 Telegram:\n"
            f"{username}\n\n"

            f"🔢 Telegram ID:\n"
            f"<code>{user['telegram_id']}</code>\n"

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

        "<b>👤 Клиент</b>\n\n"

        f"📱 Telegram:\n"
        f"{username}\n\n"

        f"🔢 Telegram ID:\n"
        f"<code>{user['telegram_id']}</code>\n\n"

        f"🏷 Имя:\n"
        f"{first_name}\n\n"

        f"📡 Подписок:\n"
        f"{user.get('subscriptions_count', 0)}\n\n"

        f"💳 Платежей:\n"
        f"{user.get('payments_count', 0)}\n\n"

        f"💰 Оплачено:\n"
        f"{user.get('total_paid', 0)} ₽\n\n"

        f"👑 Администратор:\n"
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

            "💳 <b>Платёж</b>\n\n"

            f"🆔 ID:\n"
            f"<code>{payment['id']}</code>\n\n"

            f"👤 User:\n"
            f"<code>{payment['user_id']}</code>\n\n"

            f"💰 Сумма:\n"
            f"{payment['amount']} {payment['currency']}\n\n"

            f"📌 Статус:\n"
            f"{payment['status']}\n\n"

            f"📅 Создан:\n"
            f"{payment['created_at']}\n"

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
        "📡 <b>VPN подписки</b>\n\n"
    )


    if not subscriptions:

        return (
            text +
            "Подписок нет."
        )


    for sub in subscriptions:


        text += (

            "🔐 <b>VPN клиент</b>\n\n"

            f"📧 Email:\n"
            f"<code>{sub.get('client_email', '-')}</code>\n\n"

            f"🔌 Протокол:\n"
            f"{sub['protocol'].title()}\n\n"

            f"📌 Статус:\n"
            f"{sub['status']}\n\n"

            f"📅 До:\n"
            f"{sub['expires_at']}\n"

            "────────────\n"

        )


    return text





def admin_subscription_screen(
    sub: dict,
):

    return (

        "📡 <b>VPN подписка</b>\n\n"

        f"📧 Клиент:\n"
        f"<code>{sub.get('client_email', '-')}</code>\n\n"

        f"🔌 Протокол:\n"
        f"{sub['protocol'].title()}\n\n"

        f"📌 Статус:\n"
        f"{sub['status']}\n\n"

        f"📅 Действует до:\n"
        f"{sub['expires_at']}"

    )
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
        f"\nСтраница {data['page']}/{data['pages']}"
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



def subscription_screen(
    status: str,
    expires: str,
    days_left: int,
    protocol: str,
) -> str:

    return (
        "<b>📡 Мой VPN</b>\n\n"
        f"🔌 Протокол: {protocol}\n"
        f"📌 Статус: {status}\n"
        f"📅 До: {expires}\n"
        f"⏳ Осталось дней: {days_left}"
    )



def no_subscription_screen() -> str:

    return (
        "<b>📡 Подписок нет</b>\n\n"
        "У вас нет активной VPN подписки."
    )



def buy_screen() -> str:

    return (
        "<b>💳 Покупка VPN</b>\n\n"
        "Выберите срок подписки:"
    )



def payment_screen(
    tariff: str,
    price: int | float,
) -> str:

    return (
        "<b>💳 Оплата VPN</b>\n\n"
        f"📅 Тариф: {tariff}\n"
        f"💰 Стоимость: {price} ₽\n\n"
        "Нажмите кнопку ниже для оплаты.\n"
        "После успешной оплаты VPN будет активирован автоматически."
    )



def payment_success_screen() -> str:

    return (
        "<b>✅ Оплата успешно прошла!</b>\n\n"
        "Ваш VPN доступен.\n"
        "Конфигурация отправлена ниже."
    )



def profile_screen(
    user,
) -> str:

    username = (
        f"@{user.username}"
        if user.username
        else "-"
    )

    return (
        "<b>👤 Профиль</b>\n\n"
        f"ID: <code>{user.id}</code>\n"
        f"Telegram: <code>{user.telegram_id}</code>\n"
        f"Username: {username}\n"
    )

def my_vpn_screen(
    subscription,
) -> str:

    return (
        "<b>🔐 Мой VPN</b>\n\n"
        f"🆔 ID: <code>{subscription.id}</code>\n"
        f"🔌 Протокол: {subscription.protocol}\n"
        f"📌 Статус: {subscription.status.value}\n"
        f"📅 Действует до: {subscription.expires_at}\n"
    )

def instruction_screen() -> str:

    return (
        "<b>📖 Инструкция по подключению VPN</b>\n\n"
        "1️⃣ Откройте приложение WireGuard\n"
        "2️⃣ Добавьте полученный конфиг\n"
        "3️⃣ Включите VPN\n\n"
        "Если возникли проблемы — обратитесь в поддержку."
    )

def support_screen() -> str:

    return (
        "<b>🆘 Поддержка</b>\n\n"
        "Если у вас возникли проблемы с VPN:\n\n"
        "1️⃣ Проверьте подключение к интернету\n"
        "2️⃣ Проверьте конфигурацию VPN\n"
        "3️⃣ Обратитесь к администратору"
    )
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

def instruction_screen() -> str:

    return """
        <b>📖 Инструкция по подключению JustVPN</b>

        1️⃣ <b>Скачайте файл конфигурации</b>

        После покупки VPN скачайте полученный файл:

        <code>.conf</code>

        Сохраните его на ваше устройство.
        Это ваш персональный VPN-профиль.

        ---

        2️⃣ <b>Установите приложение WireGuard</b>

        📱 <b>Android:</b>
        https://play.google.com/store/apps/details?id=com.wireguard.android

        📱 <b>iPhone / iPad:</b>
        https://apps.apple.com/app/wireguard/id1441195209

        💻 <b>Windows:</b>
        https://www.wireguard.com/install/

        💻 <b>macOS:</b>
        https://apps.apple.com/app/wireguard/id1451685025

        💻 <b>Linux:</b>
        https://www.wireguard.com/install/

        ---

        3️⃣ <b>Откройте WireGuard</b>

        После установки запустите приложение.

        Нажмите:

        ➕ <b>Добавить туннель</b>

        или

        <b>Импортировать из файла</b>

        ---

        4️⃣ <b>Добавьте конфигурацию VPN</b>

        Выберите ранее скачанный файл:

        <code>.conf</code>

        WireGuard автоматически загрузит настройки подключения.

        ---

        5️⃣ <b>Подключите VPN</b>

        Нажмите кнопку включения рядом с вашим туннелем.

        После успешного подключения появится статус:

        ✅ <b>Активно</b>

        ---

        🎉 <b>Готово!</b>

        Теперь вы можете пользоваться быстрым,
        безопасным и стабильным VPN от JustVPN.

        ❤️ Спасибо, что выбираете JustVPN!
        """
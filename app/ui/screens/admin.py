from datetime import datetime


def format_date(value):

    if not value:
        return "-"


    if isinstance(value, datetime):

        return value.strftime(
            "%d.%m.%Y %H:%M"
        )


    if isinstance(value, str):

        value = (
            value
            .replace("T", " ")
        )

        try:

            dt = datetime.fromisoformat(
                value
            )

            return dt.strftime(
                "%d.%m.%Y %H:%M"
            )

        except ValueError:

            return value[:16]


    return str(value)

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

        f"💰 Доход: {int(stats['income'])} ₽\n"
        f"📅 Сегодня: {int(stats['today_income'])} ₽\n"
        f"🛒 Сегодня оплат: {stats['today_payments']}"
    )



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



    sub = user.get(
        "current_subscription"
    )


    vpn = user.get(
        "vpn"
    )


    if sub:


        vpn_status = (

            "🟢 <b>Активна</b>\n\n"

            f"🔌 Протокол: "
            f"{sub.get('protocol','-').title()}\n"

            f"📧 Клиент: "
            f"<code>{sub.get('client_email','-')}</code>\n"

            f"📅 До: "
            f"{format_date(sub.get('expires_at'))}\n"

            f"⏳ Осталось: "
            f"{user.get('days_left',0)} дней"

        )


        if vpn:

            vpn_status += (

                "\n\n"

                "🌐 Сервер:\n"

                f"{vpn.get('server','-')} "
                f"{vpn.get('country','')}"

                "\n\n"

                "🆔 Client ID:\n"

                f"<code>{vpn.get('client_id','-')}</code>"

            )


    else:


        vpn_status = (
            "🔴 Активной подписки нет"
        )




    last_payment = user.get(
        "last_payment"
    )


    if last_payment:


        last_payment_text = (

            f"{int(last_payment.get('amount',0))} ₽\n"

            f"{format_date(last_payment.get('paid_at'))}"

        )

    else:

        last_payment_text = "-"




    return (

        "<b>👤 Клиент</b>\n\n"


        f"📱 Telegram:\n"
        f"{username}\n\n"


        f"🆔 Telegram ID:\n"
        f"<code>{user['telegram_id']}</code>\n\n"


        f"👤 Имя:\n"
        f"{first_name}\n\n"


        "📅 Регистрация:\n"
        f"{format_date(user.get('created_at'))}\n\n"


        "🌐 VPN\n\n"

        f"{vpn_status}\n\n"



        "💳 Финансы\n\n"

        f"Платежей: {user.get('payments_count',0)}\n"

        f"Оплачено: {user.get('total_paid',0)} ₽\n\n"

        "Последний платеж:\n"

        f"{last_payment_text}\n\n"



        "📊 Статистика\n\n"

        f"Всего подписок: "
        f"{user.get('subscriptions_count',0)}\n"

        f"🟢 Активных: "
        f"{user.get('active_subscriptions',0)}\n"

        f"🔴 Истекших: "
        f"{user.get('expired_subscriptions',0)}\n"

        f"⛔ Отключенных: "
        f"{user.get('disabled_subscriptions',0)}\n\n"



        f"👑 Администратор: "
        f"{'Да' if user.get('is_admin') else 'Нет'}"

    )




def admin_payments_screen(
    data: dict,
) -> str:


    payments = data.get(
        "payments",
        [],
    )


    text = (
        "<b>💳 История платежей</b>\n\n"
    )


    if not payments:

        return (
            text +
            "Платежей нет."
        )


    for payment in payments:

        username = (
            f"@{payment['username']}"
            if payment.get("username")
            else "-"
        )


        status = {
            "paid": "✅ Оплачен",
            "pending": "⏳ Ожидает",
            "failed": "❌ Ошибка",
            "canceled": "🚫 Отменён",
            "expired": "⌛ Истёк",
        }.get(
            payment["status"],
            payment["status"],
        )


        created_at = format_date(
            payment.get("created_at")
        )


        paid_at = format_date(
            payment.get("paid_at")
        )


        text += (
                "💳 <b>#{}</b> {}\n\n"

                "👤 {}\n"
                "🔌 {}\n"
                "📦 {} дней\n\n"

                "💰 {} {}\n"
                "🏦 {}\n\n"

                "📅 {}\n"
                "✅ {}\n\n"

                "🔑 <code>{}</code>\n"

                "────────────\n\n"

            ).format(
                payment["id"],
                status,

                username,

                payment["protocol"].title(),

                payment["subscription_days"],

                int(payment["amount"]),
                payment["currency"],

                payment["provider"],

                created_at,
                paid_at,

                payment.get(
                    "client_email",
                    "-"
                ),
            )


    text += (
        f"Страница {data['page']}/{data['pages']}"
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


        status = {
            "active": "🟢 Активна",
            "expired": "🔴 Истекла",
            "disabled": "⛔ Отключена",
        }.get(
            sub["status"],
            sub["status"],
        )


        protocol = (
            sub["protocol"]
            .title()
        )

        text += (

            "🔐 <b>VPN клиент</b>\n\n"

            f"🆔 ID:\n"
            f"<code>{sub['id']}</code>\n\n"

            f"📧 Email:\n"
            f"<code>{sub.get('client_email', '-')}</code>\n\n"

            f"🔌 Протокол:\n"
            f"{protocol}\n\n"

            f"📌 Статус:\n"
            f"{status}\n\n"

            f"📅 До:\n"
            f"{format_date(sub.get('expires_at'))}\n"

            "────────────\n\n"

        )


    return text




def admin_subscription_screen(
        sub: dict,
    ) -> str:


        status = {
            "active": "🟢 Активна",
            "expired": "🔴 Истекла",
            "disabled": "⛔ Отключена",
        }.get(
            sub["status"],
            sub["status"],
        )


        server = sub.get(
            "server"
        )

        country = sub.get(
            "country"
        )


        if server:

            server_text = (
                f"{server}\n"
                f"🌍 {country or '-'}"
            )

        else:

            server_text = "-"



        user = sub.get(
            "user"
        )


        username = (
            user.get("username")
            if user
            else None
        )


        first_name = (
            user.get("first_name")
            if user
            else None
        )


        telegram_id = (
            user.get("telegram_id")
            if user
            else None
        )


        if username:

            user_text = (
                f"@{username}"
            )

        elif first_name:

            user_text = (
                first_name
            )

        else:

            user_text = (
                f"ID: {telegram_id}"
                if telegram_id
                else "-"
            )

       


        return (

            "🔐 <b>VPN подписка</b>\n\n"


            f"🆔 ID:\n"
            f"<code>{sub['id']}</code>\n\n"


            f"👤 Пользователь:\n"
            f"{user_text}\n\n"


            f"📧 Клиент:\n"
            f"<code>{sub['client_email']}</code>\n\n"


            f"🔌 Протокол:\n"
            f"{sub['protocol'].title()}\n\n"


            f"🖥 Сервер:\n"
            f"{server_text}\n\n"


            f"🆔 Client ID:\n"
            f"<code>{sub.get('client_id','-')}</code>\n\n"


            f"📌 Статус:\n"
            f"{status}\n\n"


            f"📅 Создана:\n"
            f"{format_date(sub.get('created_at'))}\n\n"


            f"⏳ До:\n"
            f"{format_date(sub.get('expires_at'))}\n\n"


            f"⌛ Осталось:\n"
            f"{sub.get('days_left','-')} дней"

        )




def admin_users_page_screen(
    data: dict,
) -> str:


    total = data.get(
        "total",
        0,
    )


    return (

        "<b>👥 Пользователи</b>\n\n"

        f"Всего: {total}\n\n"

        f"📄 Страница "
        f"{data['page']}/{data['pages']}"

    )
def payment_success_screen() -> str:

    return (
        "<b>✅ Оплата успешно прошла!</b>\n\n"
        "Ваш VPN создан.\n\n"
        "📥 Конфигурация отправлена ниже."
    )


def payment_renew_success_screen(
    old_date: str,
    new_date: str,
) -> str:

    return (
        "<b>✅ Оплата успешно прошла!</b>\n\n"
        "🔄 Ваш VPN продлён.\n\n"
        f"📅 Было до:\n"
        f"{old_date}\n\n"
        f"📅 Теперь действует до:\n"
        f"{new_date}\n\n"
        "Спасибо за использование JustVPN ❤️"
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
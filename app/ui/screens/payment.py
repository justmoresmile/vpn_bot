def payment_success_screen() -> str:

    return (
        "<b>✅ Оплата успешно прошла!</b>\n\n"
        "Ваш VPN доступен.\n"
        "Конфигурация отправлена ниже."
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
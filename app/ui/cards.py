HEADER = (
    "✦ ──────────────────────── ✦\n"
    "          🛡️ <b>VPN</b>\n"
    "✦ ──────────────────────── ✦"
)

DIVIDER = (
    "✦ ──────────────────────── ✦"
)


def card(
    title: str,
    body: str = "",
    footer: str | None = None,
) -> str:

    text = (
        f"{HEADER}\n\n"
        f"{title}"
    )

    if body:
        text += f"\n\n{body}"

    if footer:
        text += (
            f"\n\n"
            f"{DIVIDER}\n\n"
            f"{footer}"
        )

    return text


def buy_card(body: str) -> str:
    return card(
        title="🚀 <b>Подключение VPN</b>",
        body=body,
        footer="👇 Выберите тариф",
    )


def payment_card(body: str) -> str:
    return card(
        title="💳 <b>Оплата</b>",
        body=body,
    )


def subscription_card(body: str) -> str:
    return card(
        title="👤 <b>Мой VPN</b>",
        body=body,
        footer="👇 Управление VPN",
    )


def instruction_card(body: str) -> str:
    return card(
        title="📖 <b>Инструкция</b>",
        body=body,
    )
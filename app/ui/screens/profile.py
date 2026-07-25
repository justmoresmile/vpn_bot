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
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📱 Telegram: <code>{user.telegram_id}</code>\n"
        f"👤 Username: {username}\n"
    )
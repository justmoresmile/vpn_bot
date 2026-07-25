from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="📊 Статистика",
        callback_data="admin_statistics",
    )

    kb.button(
        text="👤 Пользователи",
        callback_data="admin_users",
    )

    kb.button(
        text="💳 Платежи",
        callback_data="admin_payments",
    )

    kb.button(
        text="📡 Подписки",
        callback_data="admin_subscriptions",
    )

    kb.button(
        text="📢 Рассылка",
        callback_data="admin_broadcast",
    )

    kb.adjust(1)

    return kb.as_markup()
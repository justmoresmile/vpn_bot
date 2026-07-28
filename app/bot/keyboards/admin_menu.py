from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu():

    kb = InlineKeyboardBuilder()


    kb.button(
        text="🔎 Поиск пользователя",
        callback_data="admin_search_users",
    )
    kb.button(
        text="🟢 Активные",
        callback_data="admin_filter:active"
    )
    kb.button(
        text="❌ Без подписки",
        callback_data="admin_filter:no_subscription"
    )
    kb.button(
        text="🔴 Истекшие",
        callback_data="admin_filter:expired"
    )
    kb.button(
        text="👑 Админы",
        callback_data="admin_filter:admins" 
    )


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
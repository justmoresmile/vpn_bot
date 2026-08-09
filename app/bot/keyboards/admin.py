from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    
)

from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    
)





def admin_users_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back",
                )
            ]
        ]
    )


def admin_users_pages(
    users,
    page: int,
    pages: int,
):

    kb = InlineKeyboardBuilder()


    for user in users:

        username = (
            f"@{user['username']}"
            if user.get("username")
            else "без_username"
        )


        status = (
            user.get(
                "subscription_status",
                "none"
            )
        )


        status_icon = {

            "active": "🟢",

            "expired": "🔴",

            "disabled": "⛔",

            "none": "⚪",

        }.get(
            status,
            "⚪"
        )


        kb.button(

            text=f"👤 {username} {status_icon}",

            callback_data=f"admin_user:{user['id']}",

        )


    if pages > 1:


        if page > 1:

            kb.button(

                text="⬅️",

                callback_data=f"admin_users_page:{page-1}",

            )


        kb.button(

            text=f"{page}/{pages}",

            callback_data="ignore",

        )


        if page < pages:

            kb.button(

                text="➡️",

                callback_data=f"admin_users_page:{page+1}",

            )


    kb.button(

        text="🔙 Назад",

        callback_data="admin_back",

    )


    kb.adjust(1)


    return kb.as_markup()


def admin_users_result_keyboard(
    users: list,
):

    kb = InlineKeyboardBuilder()


    for user in users:

        username = (
            f"@{user['username']}"
            if user.get("username")
            else str(user["id"])
        )


        kb.button(
            text=f"👤 {username}",
            callback_data=f"admin_user:{user['id']}",
        )


    kb.button(
        text="🔙 Назад",
        callback_data="admin_back",
    )


    kb.adjust(1)


    return kb.as_markup()



def admin_user_menu(
    user_id: int,
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="➕ Создать подписку",
        callback_data=f"admin_user_create_sub:{user_id}",
    )
    
    kb.button(
        text="📡 Подписки",
        callback_data=f"admin_user_subs:{user_id}",
    )
    
    
    kb.button(
        text="💳 Платежи",
        callback_data=f"admin_user_payments:{user_id}",
    )

    
    kb.button(
        text="✉️ Написать",
        callback_data=f"admin_user_message:{user_id}",
    )


    kb.button(
        text="🔙 Назад",
        callback_data="admin_users",
    )


    kb.adjust(1)


    return kb.as_markup()



def admin_payment_menu(
    user_id: int,
):

    kb = InlineKeyboardBuilder()


    kb.button(
        text="👤 Открыть клиента",
        callback_data=f"admin_user:{user_id}",
    )


    kb.button(
        text="🔙 Назад",
        callback_data="admin_payments",
    )


    kb.adjust(1)


    return kb.as_markup()



def admin_subscriptions_keyboard(
    subscriptions: list,
):

    kb = InlineKeyboardBuilder()


    for sub in subscriptions:

        kb.button(
            text=(
                f"🔐 #{sub['id']} "
                f"{sub['protocol'].title()}"
            ),
            callback_data=f"admin_subscription:{sub['id']}",
        )


    kb.button(
        text="⬅ Назад",
        callback_data="admin_back",
    )


    kb.adjust(1)


    return kb.as_markup()



def admin_subscription_menu(
    subscription_id: int,
    user_id: int,
):

    kb = InlineKeyboardBuilder()


    kb.button(
        text="🔄 Продлить",
        callback_data=f"admin_sub_renew:{subscription_id}",
    )


    kb.button(
        text="⛔ Отключить",
        callback_data=f"admin_sub_disable:{subscription_id}",
    )


    kb.button(
        text="♻️ Восстановить",
        callback_data=f"admin_sub_restore:{subscription_id}",
    )


    kb.button(
        text="📄 Конфиг",
        callback_data=f"admin_sub_config:{subscription_id}",
    )


    kb.button(
        text="📥 Скачать файл",
        callback_data=f"admin_sub_file:{subscription_id}",
    )


    kb.button(
        text="🗑 Удалить",
        callback_data=f"admin_sub_delete:{subscription_id}",
    )


    kb.button(
        text="👤 Пользователь",
        callback_data=f"admin_user:{user_id}",
    )


    kb.button(
        text="⬅ Назад",
        callback_data=f"admin_user_subs:{user_id}",
    )


    kb.adjust(1)


    return kb.as_markup()


def admin_subscription_delete_confirm(
    subscription_id: int,
    user_id: int,
):

    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Да, удалить",
        callback_data=f"admin_sub_delete_confirm:{subscription_id}",
    )

    builder.button(
        text="❌ Отмена",
        callback_data=f"admin_subscription:{subscription_id}",
    )

    builder.adjust(1)

    return builder.as_markup()

def admin_create_subscription_menu(
        user_id: int,
    ):

    kb = InlineKeyboardBuilder()


    kb.button(
        text="📅 30 дней",
        callback_data=f"admin_create_sub:{user_id}:30",
    )

    kb.button(
        text="📅 90 дней",
        callback_data=f"admin_create_sub:{user_id}:90",
    )

    kb.button(
        text="📅 180 дней",
        callback_data=f"admin_create_sub:{user_id}:180",
    )

    kb.button(
        text="📅 365 дней",
        callback_data=f"admin_create_sub:{user_id}:365",
    )


    kb.button(
        text="🔙 Назад",
        callback_data=f"admin_user:{user_id}",
    )


    kb.adjust(1)


    return kb.as_markup()


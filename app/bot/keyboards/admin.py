from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



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
    page: int,
    pages: int,
):

    buttons = []


    if page > 1:

        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"admin_users_page:{page-1}",
            )
        )


    buttons.append(
        InlineKeyboardButton(
            text=f"{page}/{pages}",
            callback_data="none",
        )
    )


    if page < pages:

        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"admin_users_page:{page+1}",
            )
        )


    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons,
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back",
                )
            ],
        ]
    )



def admin_user_menu(
    user_id: int,
):

    kb = InlineKeyboardBuilder()


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




def admin_subscriptions_menu(
    subscription_id: int,
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
        text="🗑 Удалить",
        callback_data=f"admin_sub_delete:{subscription_id}",
    )


    kb.button(
        text="🔙 Назад",
        callback_data="admin_users",
    )


    kb.adjust(1)


    return kb.as_markup()


from aiogram.utils.keyboard import InlineKeyboardBuilder



def admin_subscriptions_keyboard(
    subscriptions: list,
):

    kb = InlineKeyboardBuilder()


    for sub in subscriptions:

        kb.button(
            text=(
                f"📡 #{sub['id']} "
                f"{sub['protocol']}"
            ),
            callback_data=f"admin_subscription:{sub['id']}",
        )


    kb.button(
        text="🔙 Назад",
        callback_data="admin_back",
    )


    kb.adjust(1)


    return kb.as_markup()




def admin_subscription_menu(
    subscription_id: int,
):

    kb = InlineKeyboardBuilder()

    kb.button(
        text="🔄 Продлить 30 дней",
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
        text="🗑 Удалить",
        callback_data=f"admin_sub_delete:{subscription_id}",
    )

    kb.button(
        text="🔙 Назад",
        callback_data="admin_subscriptions",
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
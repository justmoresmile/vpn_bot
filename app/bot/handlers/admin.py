from httpx import HTTPStatusError

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
)

from app.bot.clients.api_client import api_client

from app.bot.keyboards.admin_menu import (
    admin_menu,
)



from app.ui.screens.admin import (
    admin_users_page_screen,
    admin_user_screen,
    admin_subscription_screen,
    admin_payments_screen,
    admin_subscriptions_screen,
)

from app.bot.keyboards.admin import (
    admin_users_pages,
    admin_user_menu,
    admin_subscriptions_keyboard,
    admin_users_result_keyboard,
    admin_subscription_menu,
    admin_subscription_delete_confirm,
    admin_create_subscription_menu,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime



def format_date(value):

    if not value:
        return "-"

    if isinstance(value, datetime):
        return value.strftime(
            "%d.%m.%Y %H:%M"
        )

    if isinstance(value, str):

        return (
            value
            .replace("T", " ")
            [:16]
        )

    return str(value)

router = Router()
class AdminSearchState(StatesGroup):

    waiting_query = State()

async def show_subscription(
    callback: CallbackQuery,
    subscription_id: int,
):

    subscription = await api_client.get_admin_subscription(
        callback.from_user.id,
        subscription_id,
    )


    if not subscription:

        await callback.answer(
            "Подписка не найдена",
            show_alert=True,
        )

        return False


    print("SUB DATA:", subscription)


    await callback.message.edit_text(

        admin_subscription_screen(
            subscription
        ),

        parse_mode="HTML",

        reply_markup=admin_subscription_menu(

            subscription_id,

            subscription["user_id"],

        ),
    )


    return True


async def _is_admin(
    telegram_id: int,
) -> bool:

    try:

        await api_client.get_admin_statistics(
            telegram_id
        )

        return True


    except HTTPStatusError as e:

        if e.response.status_code == 403:

            return False

        raise




@router.message(
    F.text == "/admin"
)
async def admin_command(
    message: Message,
):

    if not await _is_admin(
        message.chat.id
    ):

        await message.answer(
            "⛔ У вас нет прав администратора."
        )

        return


    await message.answer(
        "⚙️ Панель администратора",
        reply_markup=admin_menu(),
    )





@router.callback_query(
    F.data == "admin_statistics",
)
async def admin_statistics(
    callback: CallbackQuery,
):

    if not await _is_admin(
        callback.from_user.id
    ):

        await callback.answer(
            "Нет доступа",
            show_alert=True,
        )

        return


    stats = await api_client.get_admin_statistics(
        callback.from_user.id
    )


    text = (
        "📊 <b>Статистика</b>\n\n"

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


    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )


    await callback.answer()





@router.callback_query(
    F.data == "admin_users",
)
async def admin_users(
    callback: CallbackQuery,
):

    data = await api_client.get_admin_users_page(
        callback.from_user.id,
        1,
    )


    await callback.message.edit_text(
        admin_users_page_screen(
            data
        ),
        reply_markup=admin_users_pages(
            data["users"],
            data["page"],
            data["pages"],
        ),
    )


    await callback.answer()





@router.callback_query(
    F.data.startswith(
        "admin_users_page:"
    )
)
async def admin_users_page(
    callback: CallbackQuery,
):

    page = int(
        callback.data.split(":")[1]
    )


    data = await api_client.get_admin_users_page(
        callback.from_user.id,
        page,
    )


    await callback.message.edit_text(
        admin_users_page_screen(data),
        reply_markup=admin_users_pages(
            data["users"],
            data["page"],
            data["pages"],
        ),
    )


    await callback.answer()


@router.callback_query(
    F.data == "admin_payments",
)
async def admin_payments(
    callback: CallbackQuery,
):

    data = await api_client.get_admin_payments(
        callback.from_user.id,
        1,
    )


    await callback.message.edit_text(
        admin_payments_screen(
            data
        ),
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )


    await callback.answer()


@router.callback_query(
    F.data == "admin_subscriptions",
)
async def admin_subscriptions(
    callback: CallbackQuery,
):

    data = await api_client.get_admin_subscriptions(
        callback.from_user.id,
    )


    await callback.message.edit_text(

        admin_subscriptions_screen(
            data["subscriptions"]
        ),

        parse_mode="HTML",

        reply_markup=admin_subscriptions_keyboard(
            data["subscriptions"]
        ),
    )


    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "admin_subscription:"
    )
)
async def admin_subscription(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    result = await show_subscription(
        callback,
        subscription_id,
    )

    if result:
        await callback.answer()

@router.callback_query(
    F.data == "admin_broadcast",
)
async def admin_broadcast(
    callback: CallbackQuery,
):

    await callback.answer()

    try:
        await callback.message.edit_text(
            "📢 Рассылка\n\n🚧 В разработке",
            reply_markup=admin_menu(),
        )

    except Exception:
        pass



@router.callback_query(
    F.data == "admin_back",
)
async def admin_back(
    callback: CallbackQuery,
):

    await callback.message.edit_text(

        "⚙️ Панель администратора",

        reply_markup=admin_menu(),

    )


    await callback.answer()





@router.callback_query(
    F.data.startswith(
        "admin_user:"
    )
)
async def admin_user(
    callback: CallbackQuery,
):

    user_id = int(
        callback.data.split(":")[1]
    )


    card = await api_client.get_admin_user_card(
    callback.from_user.id,
    user_id,
    )
    

    await callback.message.edit_text(

        admin_user_screen(
            card
        ),

        parse_mode="HTML",

        reply_markup=admin_user_menu(
            user_id
        ),

    )


    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "admin_user_subs:"
    )
)
async def admin_user_subs(
    callback: CallbackQuery,
):

    # сразу закрываем callback,
    # чтобы Telegram не протухал
    await callback.answer()


    user_id = int(
        callback.data.split(":")[1]
    )


    subscriptions = await api_client.get_admin_user_subscriptions(
        callback.from_user.id,
        user_id,
    )


    if not subscriptions:

        text = (
            "📡 <b>Подписки пользователя</b>\n\n"
            "У пользователя пока нет подписок."
        )

    else:

        text = (
            "📡 <b>Подписки пользователя</b>\n\n"
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


            text += (

                f"🔐 <b>Подписка #{sub['id']}</b>\n\n"

                f"📧 <code>{sub.get('client_email', '-')}</code>\n"

                f"🔌 {sub['protocol'].title()}\n"

                f"📌 {status}\n"

                f"📅 До: {format_date(sub['expires_at'])}\n\n"

                "────────────\n\n"

            )


        text += (
            "👇 Выберите подписку кнопками ниже"
        )


    try:

        await callback.message.edit_text(

            text,

            parse_mode="HTML",

            reply_markup=admin_subscriptions_keyboard(
                subscriptions
            ),

        )


    except Exception as e:

        if "message is not modified" not in str(e):
            raise



@router.callback_query(
    F.data.startswith(
        "admin_user_payments:"
    )
)
async def admin_user_payments(
    callback: CallbackQuery,
):

    user_id = int(
        callback.data.split(":")[1]
    )


    payments = await api_client.get_admin_user_payments(
        callback.from_user.id,
        user_id,
    )


    if not payments:

        text = (
            "💳 Платежей нет"
        )

    else:

        text = (
            "💳 <b>Платежи пользователя</b>\n\n"
        )


        for payment in payments:
            if isinstance(payment["created_at"], str):

                payment["created_at"] = datetime.fromisoformat(
                    payment["created_at"]
                )


            if payment.get("paid_at") and isinstance(payment["paid_at"], str):

                payment["paid_at"] = datetime.fromisoformat(
                    payment["paid_at"]
                )
            text += (
                f"🆔 ID: <code>{payment['id']}</code>\n"
                f"💰 Сумма: {payment['amount']} {payment['currency']}\n"
                f"📌 Статус: {payment['status']}\n"
                f"🔌 Протокол: {payment.get('protocol', '-')}\n"
                f"📅 Дней: {payment.get('subscription_days', '-')}\n"
                f"🕒 Создан: {payment['created_at']}\n\n"
            )


    try:

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=admin_user_menu(
                user_id
            ),
        )

    except Exception as e:

        if "message is not modified" not in str(e):
            raise


    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "admin_user_create_sub:"
    )
)
async def admin_user_create_sub(
    callback: CallbackQuery,
):

    user_id = int(
        callback.data.split(":")[1]
    )


    await callback.message.edit_text(
        "➕ <b>Создание подписки</b>\n\n"
        "Выберите срок подписки:",
        parse_mode="HTML",
        reply_markup=admin_create_subscription_menu(
            user_id
        ),
    )


    await callback.answer()


@router.callback_query(
    F.data.startswith(
        "admin_create_sub:"
    )
)
async def admin_create_sub(
    callback: CallbackQuery,
):

    _, user_id, days = callback.data.split(":")


    user_id = int(user_id)
    days = int(days)


    await callback.answer(
        "Создаю подписку..."
    )


    result = await api_client.create_admin_subscription(
        callback.from_user.id,
        user_id,
        days,
    )


    await callback.message.edit_text(

        "✅ <b>Подписка создана</b>\n\n"

        f"👤 Пользователь: <code>{user_id}</code>\n"
        f"📅 Срок: {days} дней",

        parse_mode="HTML",

        reply_markup=admin_user_menu(
            user_id
        ),

    )



@router.callback_query(
    F.data.startswith("admin_sub_renew:")
)
async def admin_subscription_renew(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )


    await api_client.renew_subscription(
        callback.from_user.id,
        subscription_id,
        30,
    )


    await show_subscription(
        callback,
        subscription_id,
    )


    await callback.answer(
        "✅ Подписка продлена на 30 дней"
    )

@router.callback_query(
    F.data.startswith("admin_sub_disable:")
)
async def admin_sub_disable(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    await api_client.disable_subscription(
        callback.from_user.id,
        subscription_id,
    )

    await show_subscription(
        callback,
        subscription_id,
    )

    await callback.answer(
        "⛔ Подписка отключена"
    )


@router.callback_query(
    F.data.startswith("admin_sub_restore:")
)
async def admin_sub_restore(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    await api_client.restore_subscription(
        callback.from_user.id,
        subscription_id,
    )

    await show_subscription(
        callback,
        subscription_id,
    )

    await callback.answer(
        "♻️ Подписка восстановлена"
    )

@router.callback_query(
    F.data.startswith("admin_sub_delete:")
)
async def admin_sub_delete(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    subscription = await api_client.get_admin_subscription(
        callback.from_user.id,
        subscription_id,
    )

    await callback.message.edit_text(
        "⚠️ <b>Удаление подписки</b>\n\n"
        "Это действие нельзя отменить.\n\n"
        "Вы уверены?",
        parse_mode="HTML",
        reply_markup=admin_subscription_delete_confirm(
            subscription_id,
            subscription["user_id"],
        ),
    )

    await callback.answer()

@router.callback_query(
    F.data.startswith("admin_sub_delete_confirm:")
)
async def admin_sub_delete_confirm(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )

    await api_client.delete_subscription(
        callback.from_user.id,
        subscription_id,
    )

    data = await api_client.get_admin_subscriptions(
        callback.from_user.id,
    )

    await callback.message.edit_text(
        admin_subscriptions_screen(
            data["subscriptions"]
        ),
        parse_mode="HTML",
        reply_markup=admin_subscriptions_keyboard(
            data["subscriptions"]
        ),
    )

    await callback.answer(
        "🗑 Подписка удалена"
    )


@router.callback_query(
    F.data.startswith("admin_sub_config:")
)
async def admin_sub_config(
    callback: CallbackQuery,
):
    subscription_id = int(
        callback.data.split(":")[1]
    )

    config = await api_client.get_subscription_config(
        callback.from_user.id,
        subscription_id,
    )

    if not config or not config.get("config"):
        await callback.answer(
            "Конфигурация не найдена",
            show_alert=True,
        )
        return

    subscription = await api_client.get_admin_subscription(
        callback.from_user.id,
        subscription_id,
    )

    if not subscription:
        await callback.answer(
            "Подписка не найдена",
            show_alert=True,
        )
        return

    protocol = subscription.get(
        "protocol",
        ""
    ).lower()

    value = config["config"]

    if protocol == "vless":
        text = (
            "🔗 <b>VLESS ссылка</b>\n\n"
            f"<code>{value}</code>\n\n"
            "👆 Нажмите на ссылку, чтобы скопировать её."
        )
    else:
        text = (
            "📄 <b>Конфигурация</b>\n\n"
            f"<code>{value}</code>"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML",
    )

    await callback.answer()






@router.callback_query(
    F.data.startswith("admin_sub_file:")
)
async def admin_sub_file(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )


    file = await api_client.get_subscription_file(
        callback.from_user.id,
        subscription_id,
    )


    subscription = await api_client.get_admin_subscription(
        callback.from_user.id,
        subscription_id,
    )


    await callback.message.answer_document(
        document=BufferedInputFile(
            file.content,
            filename=f"{subscription['client_email']}.conf",
        )
    )


    await callback.answer()

@router.callback_query(
    F.data == "admin_search_users"
)
async def admin_search_start(
    callback: CallbackQuery,
    state: FSMContext,
):

    await state.set_state(
        AdminSearchState.waiting_query
    )

    await callback.message.answer(
        "🔎 Введите username, имя или Telegram ID:"
    )

    await callback.answer()



@router.message(
    AdminSearchState.waiting_query
)
async def admin_search_result(
    message: Message,
    state: FSMContext,
):

    query = message.text


    users = await api_client.search_users(
        message.from_user.id,
        query,
    )


    if not users:

        await message.answer(
            "❌ Пользователи не найдены",
            reply_markup=admin_menu(),
        )

        await state.clear()

        return



    text = (
        "🔎 <b>Результаты поиска</b>\n\n"
    )


    for user in users:

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

        text += (
            f"👤 ID: <code>{user['id']}</code>\n"
            f"📱 TG: <code>{user['telegram_id']}</code>\n"
            f"Username: {username}\n"
            f"Имя: {first_name}\n\n"
        )


    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=admin_users_result_keyboard(
            [
                {
                    "id": user["id"],
                    "username": user.get("username") or "no_username",
                }
                for user in users
            ]
        ),
    )


    await state.clear()

@router.callback_query(
    F.data.startswith("admin_filter:")
)
async def admin_filter_users(
    callback: CallbackQuery,
):

    filter_type = callback.data.split(":")[1]

    titles = {
        "active": "🟢 Активные пользователи",
        "no_subscription": "❌ Пользователи без подписки",
        "expired": "🔴 Истекшие подписки",
        "admins": "👑 Администраторы",
    }

    if filter_type not in titles:

        await callback.answer(
            "Неизвестный фильтр"
        )

        return

    users = await api_client.filter_users(
        callback.from_user.id,
        filter_type,
    )

    title = titles[filter_type]

    


    if not users:

        text = (
            f"{title}\n\n"
            "Пользователей нет"
        )

    else:

        text = (
            f"<b>{title}</b>\n\n"
        )


        for user in users:

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


            text += (
                f"👤 ID: <code>{user['id']}</code>\n"
                f"📱 TG: <code>{user['telegram_id']}</code>\n"
                f"Username: {username}\n"
                f"Имя: {first_name}\n\n"
            )


    try:

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=admin_users_result_keyboard(
                [
                    {
                        "id": user["id"],
                        "username": user.get("username") or "no_username",
                    }
                    for user in users
                ]
            ),
        )

    except Exception as e:

        if "message is not modified" not in str(e):
            raise


    await callback.answer()
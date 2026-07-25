from httpx import HTTPStatusError

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)

from app.bot.clients.api_client import api_client

from app.bot.keyboards.admin_menu import (
    admin_menu,
)

from app.bot.keyboards.admin import (
    admin_users_pages,
    admin_user_menu,
    admin_subscription_menu,
)


from app.ui.screens.admin import (
    admin_users_page_screen,
    admin_user_screen,
    admin_subscription_screen,
)

from app.ui.screens.admin import (
    admin_users_page_screen,
    admin_user_screen,
    admin_payments_screen,
    admin_subscriptions_screen,
)

router = Router()



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
        admin_users_page_screen(
            data
        ),
        reply_markup=admin_users_pages(
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

    subscriptions = await api_client.get_admin_subscriptions(
        callback.from_user.id
    )


    text = admin_subscriptions_screen(
        subscriptions
    )


    try:

        from app.bot.keyboards.admin import (
    admin_subscriptions_keyboard,
)


        await callback.message.edit_text(
            admin_subscriptions_screen(
                subscriptions
            ),
            parse_mode="HTML",
            reply_markup=admin_subscriptions_keyboard(
                subscriptions
            ),
        )

    except Exception as e:

        if "message is not modified" not in str(e):

            raise


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


    user = await api_client.get_admin_user(
        callback.from_user.id,
        user_id,
    )


    await callback.message.edit_text(

        admin_user_screen(
            user
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

    user_id = int(
        callback.data.split(":")[1]
    )


    subscriptions = await api_client.get_admin_user_subscriptions(
        callback.from_user.id,
        user_id,
    )


    if not subscriptions:

        text = (
            "📡 Подписок нет"
        )


    else:

        text = (
            "📡 <b>Подписки пользователя</b>\n\n"
        )


        for sub in subscriptions:

            text += (

                f"ID: <code>{sub['id']}</code>\n"

                f"Протокол: {sub['protocol']}\n"

                f"Статус: {sub['status']}\n"

                f"До: {sub['expires_at']}\n\n"

            )


    await callback.message.edit_text(

        text,

        parse_mode="HTML",

        reply_markup=admin_user_menu(
            user_id
        ),

    )


    await callback.answer()


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

            text += (
                f"🆔 ID: <code>{payment['id']}</code>\n"
                f"💰 Сумма: {payment['amount']} {payment['currency']}\n"
                f"📌 Статус: {payment['status']}\n"
                f"🔌 Протокол: {payment.get('protocol', '-')}\n"
                f"📅 Дней: {payment.get('subscription_days', '-')}\n"
                f"🕒 Создан: {payment['created_at']}\n\n"
            )


    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=admin_user_menu(
            user_id
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


    subscriptions = await api_client.get_admin_subscriptions(
        callback.from_user.id
    )


    subscription = next(
        (
            sub
            for sub in subscriptions
            if sub["id"] == subscription_id
        ),
        None,
    )


    if subscription is None:

        await callback.answer(
            "Подписка не найдена",
            show_alert=True,
        )

        return



    await callback.message.edit_text(

        admin_subscription_screen(
            subscription
        ),

        parse_mode="HTML",

        reply_markup=admin_subscription_menu(
            subscription_id
        ),
    )


    await callback.answer()


@router.callback_query(
F.data.startswith(
    "admin_sub_renew:"
)
)
async def admin_subscription_renew(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )


    result = await api_client.renew_subscription(
        callback.from_user.id,
        subscription_id,
        30,
    )


    await callback.answer(
        "✅ Подписка продлена на 30 дней",
        show_alert=True,
    )


    subscriptions = await api_client.get_admin_subscriptions(
        callback.from_user.id
    )


    subscription = next(
        (
            sub
            for sub in subscriptions
            if sub["id"] == subscription_id
        ),
        None,
    )


    if subscription:

        await callback.message.edit_text(
            admin_subscription_screen(
                subscription
            ),
            parse_mode="HTML",
            reply_markup=admin_subscription_menu(
                subscription_id
            ),
        )


@router.callback_query(
F.data.startswith("admin_sub_renew:")
)
async def admin_sub_renew(
    callback: CallbackQuery,
):

    subscription_id = int(
        callback.data.split(":")[1]
    )


    result = await api_client.renew_subscription(
        callback.from_user.id,
        subscription_id,
        30,
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


    await api_client.delete_subscription(
        callback.from_user.id,
        subscription_id,
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


    text = (
        "📄 <b>Конфигурация</b>\n\n"
        f"<code>{config['config']}</code>"
    )


    await callback.message.answer(
        text,
        parse_mode="HTML",
    )


    await callback.answer()
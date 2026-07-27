def instruction_screen() -> str:

    return """
        <b>📖 Инструкция по подключению JustVPN</b>

        1️⃣ <b>Скачайте файл конфигурации</b>

        После покупки VPN скачайте полученный файл:

        <code>.conf</code>

        Сохраните его на ваше устройство.
        Это ваш персональный VPN-профиль.

        ---

        2️⃣ <b>Установите приложение WireGuard</b>

        📱 <b>Android:</b>
        https://play.google.com/store/apps/details?id=com.wireguard.android

        📱 <b>iPhone / iPad:</b>
        https://apps.apple.com/app/wireguard/id1441195209

        💻 <b>Windows:</b>
        https://www.wireguard.com/install/

        💻 <b>macOS:</b>
        https://apps.apple.com/app/wireguard/id1451685025

        💻 <b>Linux:</b>
        https://www.wireguard.com/install/

        ---

        3️⃣ <b>Откройте WireGuard</b>

        После установки запустите приложение.

        Нажмите:

        ➕ <b>Добавить туннель</b>

        или

        <b>Импортировать из файла</b>

        ---

        4️⃣ <b>Добавьте конфигурацию VPN</b>

        Выберите ранее скачанный файл:

        <code>.conf</code>

        WireGuard автоматически загрузит настройки подключения.

        ---

        5️⃣ <b>Подключите VPN</b>

        Нажмите кнопку включения рядом с вашим туннелем.

        После успешного подключения появится статус:

        ✅ <b>Активно</b>

        ---

        🎉 <b>Готово!</b>

        Теперь вы можете пользоваться быстрым,
        безопасным и стабильным VPN от JustVPN.

        ❤️ Спасибо, что выбираете JustVPN!
        """




def support_screen() -> str:

    return (
        "<b>🆘 Поддержка</b>\n\n"
        "Если возникли проблемы с VPN,\n"
        "обратитесь к администратору."
    )
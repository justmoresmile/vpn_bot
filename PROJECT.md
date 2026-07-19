# VPN Bot

Telegram-бот для продажи и управления VPN-подписками через панель **3x-ui**.

Проект построен по принципу разделения ответственности и позволяет добавлять новые VPN-протоколы без изменения бизнес-логики.

---

# Текущий статус проекта

## Готовность

### Инфраструктура

- ✅ GitHub Repository
- ✅ Production VPS (Ubuntu 24.04)
- ✅ Git-деплой
- ✅ systemd сервис
- ✅ Автоматический запуск после перезагрузки
- ✅ SQLite
- ✅ Production .env
- ✅ Виртуальное окружение Python

---

### Telegram

- ✅ регистрация пользователей
- ✅ профиль пользователя
- ✅ выбор VPN-протокола
- ✅ получение конфигурации
- ✅ получение WireGuard `.conf`
- ✅ получение QR-кода
- ✅ продление подписки
- ✅ автоматическое отключение
- ✅ восстановление клиента

---

### VPN

Поддерживаются:

- ✅ VLESS Reality
- ✅ WireGuard

Работа осуществляется через официальный API **3x-ui**.

---

# Архитектура

```
Telegram
      │
      ▼
Handlers
      │
      ▼
VPNService
      │
      ▼
ProtocolHandler
      │
 ┌────┴────┐
 ▼         ▼
VLESS   WireGuard
      │
      ▼
XUIClient
      │
      ▼
3x-ui API
```

---

# Структура проекта

```
app/

    bot/
        handlers/
        keyboards/

    config/

    database/

    domain/

        subscription.py
        inbound.py
        enums.py

    protocols/

        handlers/

            base.py
            vless.py
            wireguard.py

        wireguard/

            link_parser.py

    repositories/

        subscription_repository.py
        user_repository.py

    services/

        vpn_service.py
        sync_service.py
        xui_client.py
        qr_service.py

    tasks/

    utils/
```

---

# Архитектурные принципы

Проект разделён на несколько независимых слоёв.

## Telegram

Отвечает только за взаимодействие с пользователем.

Не содержит бизнес-логики.

---

## VPNService

Главный сервис приложения.

Отвечает за:

- создание подписки
- продление
- восстановление
- отключение
- синхронизацию

Не знает ничего о Telegram и 3x-ui.

---

## ProtocolHandler

Базовый класс всех VPN-протоколов.

Поддерживает автоматическую регистрацию обработчиков.

Каждый новый протокол наследуется только от него.

Методы:

```
create_subscription()

renew()

restore_client()

disable()

sync()

delete()

build_payload()

build_config()
```

---

## XUIClient

Инкапсулирует всю работу с API панели.

Содержит только HTTP-запросы.

Не содержит бизнес-логики.

Поддерживает:

```
get_inbounds()

refresh_inbound()

add_client()

update_client()

delete_client()

get_client()

set_client_enabled()

get_subscription_links()

get_wireguard_config()
```

---

## Repository

Работает исключительно с SQLite.

Не содержит логики приложения.

---

# Поддерживаемые протоколы

## VLESS Reality

Полностью реализовано.

Используется официальный механизм 3x-ui.

Поддерживается:

- создание клиента
- продление
- отключение
- восстановление
- удаление
- синхронизация
- получение subscription link
- автоматическое обновление конфигурации

---

## WireGuard

Полностью реализовано.

Поддерживается:

- создание клиента
- продление
- отключение
- восстановление
- удаление
- синхронизация
- получение subscription link
- преобразование в `.conf`
- получение QR-кода

---

# База данных

## users

```
id
telegram_id
username
first_name
is_admin
```

---

## subscriptions

```
id
user_id

protocol
inbound_id

client_uuid
client_email

sub_id

config

status

created_at
expires_at
```

---

## payments

```
id
user_id

amount
currency

provider
status

created_at
```

---

# Production

Развёртывание производится на Ubuntu 24.

Используется:

```
GitHub

↓

git pull

↓

Python venv

↓

systemd

↓

Telegram Bot
```

Обновление новой версии:

```
git pull

source .venv/bin/activate

pip install -r requirements.txt

sudo systemctl restart vpnbot
```

---

# Ближайшие задачи (Release 1.0)

## Приоритет 1

- ⏳ интеграция ЮKassa
- ⏳ обработка Webhook
- ⏳ автоматическая выдача VPN после оплаты
- ⏳ запись платежей в БД

---

## Приоритет 2

- уведомления об окончании подписки
- продление после оплаты
- история платежей

---

## Release 1.1

- Shadowsocks
- Trojan
- Hysteria2

---

## Release 2.0

- админ-панель
- статистика
- мультисерверность
- Telegram Stars
- CryptoBot
- Stripe

---

# Основная идея проекта

Максимально разделить:

- Telegram
- бизнес-логику
- VPN-протоколы
- работу с 3x-ui
- хранение данных

Это позволяет добавлять новые протоколы и новые способы оплаты без изменения существующей архитектуры.

---

# Текущая готовность

Инфраструктура: **100%**

Архитектура: **95%**

VPN-функциональность: **95%**

Production: **100%**

Платежная система: **0%**

Общая готовность проекта к релизу: **≈85%**
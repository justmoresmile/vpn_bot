# VPN Bot — Project Documentation

## Общая информация

Проект представляет собой Telegram-бот для продажи и управления VPN-подписками.

Архитектура построена по принципу разделения ответственности (Domain → Services → Protocols → Infrastructure) и позволяет легко добавлять новые VPN-протоколы без изменения бизнес-логики.

---

# Основные возможности

## Пользователи

* регистрация пользователей
* покупка VPN
* продление подписки
* автоматическое отключение
* автоматическое восстановление клиента
* получение конфигурации
* получение файла WireGuard
* выбор VPN-протокола

---

## Поддерживаемые протоколы

### VLESS Reality

Полностью интегрирован.

Используется официальный механизм 3x-ui:

* создание клиента
* получение subId
* получение ссылки через `/clients/subLinks/{subId}`
* автоматическое обновление ссылки
* синхронизация

Ручная сборка ссылки больше не используется.

---

### WireGuard

Полностью интегрирован.

Используется официальный механизм 3x-ui:

* создание клиента
* получение subId
* получение subscription link
* преобразование ссылки в `.conf`
* автоматическое обновление конфига

Получение конфига полностью централизовано внутри `XUIClient`.

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

    utils/
```

---

# Domain

## Subscription

Содержит данные клиента.

Поля:

```
id
user_id

protocol
inbound_id

client_id
client_email

sub_id

config

status

created_at
expires_at
```

`sub_id` используется только VLESS.

Для остальных протоколов может быть `None`.

---

## Inbound

Описание inbound панели.

```
id
protocol
remark
port
raw
```

---

# ProtocolHandler

Базовый класс всех VPN-протоколов.

Поддерживает автоматическую регистрацию обработчиков.

Методы:

```
get_inbound()

build_payload()

build_config()

create_subscription()

restore_client()

renew()

disable()

sync()

delete()
```

Все новые протоколы наследуются только от него.

---

# VPNService

Отвечает исключительно за бизнес-логику.

Не знает ничего о 3x-ui.

Использует:

```
ProtocolHandler.create(protocol)
```

После любой операции сохраняет изменения в БД.

---

# XUIClient

Инкапсулирует всю работу с API панели.

Поддерживает:

```
get_inbounds()

get_inbound()

refresh_inbound()

add_client()

update_client()

delete_client()

get_client()

get_wireguard_client()

get_subscription_links()

get_wireguard_config()

set_client_enabled()
```

Бизнес-логики здесь нет.

Только API.

---

# SubscriptionRepository

Работает исключительно с SQLite.

Поддерживает:

```
create()

update()

delete()

get_all()

get_by_user()

get_active_by_user()

get_latest_by_user()

get_expired_active()
```

---

# SyncService

Регулярная синхронизация клиентов.

Алгоритм:

```
получить подписки

↓

для каждой

↓

VPNService.sync_subscription()

↓

handler.sync()

↓

обновить SQLite
```

---

# Что уже реализовано

## VLESS

✔ создание клиента

✔ продление

✔ восстановление

✔ отключение

✔ удаление

✔ синхронизация

✔ автоматическое получение subId

✔ получение ссылки через 3x-ui

✔ сохранение subId

✔ автоматическое обновление ссылки

---

## WireGuard

✔ создание клиента

✔ продление

✔ восстановление

✔ отключение

✔ удаление

✔ синхронизация

✔ получение subscription link

✔ преобразование ссылки в `.conf`

✔ единый метод получения конфига

---

# Что планируется

## 1. Shadowsocks

Добавить новый ProtocolHandler.

---

## 2. Trojan

Добавить новый ProtocolHandler.

---

## 3. Hysteria2

Добавить новый ProtocolHandler.

---

## 4. Админ-панель

Функции:

* просмотр пользователей
* просмотр подписок
* создание подписок
* удаление
* рассылка
* статистика

---

## 5. Статистика

Показатели:

* активные подписки
* продажи
* новые пользователи
* выручка
* количество клиентов по протоколам

---

## 6. Платежные системы

Подключение:

* ЮKassa
* Telegram Stars
* CryptoBot
* Stripe (при необходимости)

---

## 7. Планировщик

Автоматические задачи:

* отключение подписок
* синхронизация
* уведомления
* резервное копирование

---

## 8. Экспорт

Поддержка:

* QR-коды
* ссылки
* WireGuard `.conf`
* ZIP-пакеты конфигураций

---

## 9. Мультисерверность

Поддержка нескольких серверов.

Выбор:

* по стране
* по нагрузке
* по протоколу

---

# Главная идея проекта

Максимально отделить:

* Telegram
* бизнес-логику
* VPN-протоколы
* работу с 3x-ui
* базу данных

Такой подход позволяет добавлять новые протоколы и функциональность без изменения существующего кода и с минимальным количеством дублирования.

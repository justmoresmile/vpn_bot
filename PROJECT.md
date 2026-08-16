# JustVPN — Project State & Development Context

**Project:** JustVPN
**Repository:** `git@github.com:justmoresmile/vpn_bot.git`
**Branch:** `main`
**Server path:** `/opt/vpn-bot`
**Current project state:** Backend + Telegram Bot + Admin API + Mini App + 3x-ui/VLESS integration
**Last context update:** 2026-08-16

---

# 1. PURPOSE OF THIS FILE

This file is the permanent development context for JustVPN.

Before making architectural changes:

1. Read this file.
2. Check the actual repository state.
3. Do not reintroduce already removed architecture.
4. Do not move business logic into Telegram Bot or Mini App.
5. Do not bypass Backend API from clients.
6. Update this file after significant architectural changes.

The project is developed incrementally across multiple ChatGPT conversations.

This file exists so development can continue in a new chat without losing the project architecture, decisions, current state, or next steps.

---

# 2. PROJECT GOAL

JustVPN is a commercial VPN service.

Current clients:

* Telegram Bot
* Telegram Mini App
* Admin Web Panel / API
* Android client
* future iOS client
* future Desktop client
* future Android TV client

The intended architecture is:

```text
                    ┌─────────────────────┐
                    │    Telegram Bot     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Telegram MiniApp  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Backend API      │
                    │      FastAPI        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
      ┌───────▼───────┐ ┌──────▼───────┐ ┌─────▼─────────┐
      │   Services    │ │ Repositories  │ │   Payments    │
      └───────┬───────┘ └──────┬───────┘ └───────────────┘
              │                │
              └────────┬───────┘
                       │
                ┌──────▼──────┐
                │   SQLite DB  │
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │    3x-ui     │
                │    X-UI      │
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │     Xray     │
                │    VLESS     │
                └──────────────┘
```

The most important architectural rule:

> Clients communicate with the Backend API. Business logic must not be duplicated inside Telegram Bot, Mini App, or Android.

---

# 3. CURRENT PROTOCOL ARCHITECTURE

The project uses a plugin/handler architecture for VPN protocols.

Location:

```text
app/protocols/
├── __init__.py
├── loader.py
├── handlers/
│   ├── __init__.py
│   ├── base.py
│   ├── vless.py
│   └── wireguard.py
└── wireguard/
    └── link_parser.py
```

Protocols are loaded dynamically.

`app/protocols/loader.py` discovers handlers from:

```text
app/protocols/handlers/
```

and registers them through the protocol handler registry.

---

# 4. PROTOCOL DECISION

## VLESS

VLESS is currently the main user-facing protocol.

Current intended use:

* Telegram Bot
* Telegram Mini App
* subscription system
* future clients where appropriate

VLESS is integrated through 3x-ui/Xray.

The Telegram user should currently receive VLESS rather than WireGuard.

---

## WireGuard

WireGuard remains in the architecture.

It is NOT being removed.

Current intended purpose:

* Android client
* future native clients
* possible future protocol switching

The project should therefore keep WireGuard support in the protocol layer even though VLESS is currently the primary user-facing protocol.

---

# 5. 3X-UI / XRAY

Current panel:

```text
3x-ui
```

Version:

```text
3.6.0
```

Systemd service:

```text
x-ui.service
```

Executable:

```text
/usr/local/x-ui/x-ui
```

Working directory:

```text
/usr/local/x-ui/
```

The project communicates with 3x-ui through:

```text
app/services/xui_client.py
```

The higher-level VPN abstraction is:

```text
app/services/vpn_service.py
```

`VPNService` maintains XUI clients and selects protocol handlers.

---

# 6. CURRENT XUI ARCHITECTURE

Main classes/components:

```text
XUIClient
VPNService
ProtocolHandler
VLESSHandler
WireGuardHandler
```

Expected flow:

```text
API / Service
     │
     ▼
VPNService
     │
     ├── protocol = vless
     │        │
     │        ▼
     │   VLESSHandler
     │        │
     │        ▼
     │     XUIClient
     │        │
     │        ▼
     │      3x-ui
     │
     └── protocol = wireguard
              │
              ▼
        WireGuardHandler
```

The current working tree has uncommitted modifications in:

```text
app/protocols/handlers/vless.py
app/services/xui_client.py
```

These changes must be reviewed before the next commit.

---

# 7. DATABASE

Database engine:

```text
SQLite
```

Production database:

```text
/opt/vpn-bot/data/vpn.db
```

Configured through:

```text
DATABASE_PATH
```

Database implementation:

```text
app/database/database.py
```

Schema:

```text
app/database/schema.py
```

Database initialization:

```text
scripts/init_db.py
```

SQLite settings currently include:

```text
WAL
synchronous=NORMAL
foreign_keys=ON
timeout=30
```

---

# 8. DATABASE TABLES

## users

Current fields:

```text
id
telegram_id
username
first_name
is_admin
is_blocked
api_key
created_at
```

---

## servers

Current fields:

```text
id
name
country
host
api_url
api_token
wireguard_inbound_id
enabled
priority
```

Important:

The server table is used so VPN infrastructure is not hardcoded into the bot.

---

## subscriptions

Current fields:

```text
id
user_id
server_id
protocol
inbound_id
client_uuid
client_email
sub_id
subscription_token
config
status
created_at
expires_at
```

Relations:

```text
subscriptions.user_id → users.id
subscriptions.server_id → servers.id
```

---

## payments

Current fields:

```text
id
user_id
protocol
subscription_days
subscription_id
amount
currency
status
provider
provider_payment_id
confirmation_url
created_at
paid_at
updated_at
```

Payment provider:

```text
YooKassa
```

---

## subscription_notifications

Current fields:

```text
id
subscription_id
notification_type
expires_at
created_at
```

Unique constraint:

```text
(subscription_id, notification_type, expires_at)
```

---

# 9. DATABASE ACCESS RULE

Repositories are responsible for database access.

Repositories currently include:

```text
app/repositories/
├── payment_repository.py
├── server_repository.py
├── subscription_notification_repository.py
├── subscription_repository.py
└── user_repository.py
```

Services should contain business logic.

Routers should handle HTTP/API concerns.

Telegram handlers should handle Telegram/UI concerns.

Do NOT add direct SQLite access to Telegram handlers.

---

# 10. BACKEND API

Main API architecture:

```text
app/api/
├── server.py
├── routers.py
├── backend_client.py
├── client.py
├── dependencies/
└── routes/
```

Routes include:

```text
health
auth
internal
admin
user
subscription
purchase
payment
public_subscription
vpn
```

The Backend API is the central integration point for all clients.

---

# 11. AUTHENTICATION

Authentication layers include:

```text
API Key
JWT
Telegram WebApp authentication
```

Relevant files:

```text
app/services/auth/auth_service.py
app/services/auth/jwt_service.py
app/services/auth/telegram_webapp_auth.py
app/api/dependencies/auth.py
app/api/dependencies/admin.py
app/api/dependencies/internal.py
```

JWT settings are stored in `.env`.

Secrets must never be hardcoded in source code.

---

# 12. TELEGRAM BOT

Bot architecture:

```text
app/bot/
```

Important files:

```text
app/bot/app.py
app/bot/bot_instance.py
app/bot/routers.py
```

Handlers:

```text
account.py
admin.py
buy.py
instruction.py
profile.py
start.py
subscription_actions.py
subscriptions.py
support.py
```

Keyboards:

```text
admin.py
admin_menu.py
buy_menu.py
main_menu.py
miniapp.py
protocol_menu.py
subscription_menu.py
support_menu.py
tariff_menu.py
```

The Bot must not become the main business-logic layer.

---

# 13. TELEGRAM USER FLOW

Expected general flow:

```text
User
  │
  ▼
Telegram Bot
  │
  ▼
Backend API
  │
  ├── User
  ├── Subscription
  ├── Payment
  └── VPN Service
           │
           ▼
         3x-ui
```

For VLESS, the user receives a subscription URL/config generated by the backend.

---

# 14. TELEGRAM MINI APP

Mini App source:

```text
miniapp/
```

Technology:

```text
React
TypeScript
Vite
```

Important files:

```text
miniapp/src/App.tsx
miniapp/src/App.css
miniapp/src/index.css
miniapp/src/api/
miniapp/src/context/
miniapp/src/pages/
miniapp/src/theme/
```

Current theme architecture:

```text
ThemeContext
themes
```

Current branding assets include:

```text
justfastvpn-icon.png
justfastvpn-logo-dark.png
justfastvpn-logo-transparent.png
justfastvpn-logo-white.png
```

The Mini App should use the Backend API rather than directly accessing SQLite or 3x-ui.

---

# 15. ANDROID CLIENT

Android project exists separately.

Technology:

```text
Kotlin
Jetpack Compose
Material3
Retrofit
WireGuard GoBackend
```

Minimum SDK:

```text
26
```

Android architecture includes:

```text
ApiClient
TokenStorage
AuthRepository
UserRepository
SubscriptionRepository
VpnRepository
VpnViewModel
HomeViewModel
WireGuardManager
GoBackend
```

WireGuard remains important for the native Android client.

VLESS should be implemented at the shared backend/core architecture level rather than by deleting WireGuard.

---

# 16. PAYMENT SYSTEM

Provider:

```text
YooKassa
```

Relevant file:

```text
app/payments/yookassa_client.py
```

Payment service:

```text
app/services/payment_service.py
```

Webhook:

```text
POST /payments/yookassa/webhook
```

Successful payment event:

```text
payment.succeeded
```

Current tariff values previously established:

```text
30 days  = 299
90 days  = 799
180 days = 1499
365 days = 2499
```

Payment lifecycle must remain:

```text
create payment
     │
     ▼
pending
     │
     ▼
YooKassa
     │
     ▼
webhook
     │
     ▼
payment.succeeded
     │
     ▼
subscription creation/extension
     │
     ▼
VPN client expiry update
```

---

# 17. SUBSCRIPTION SYSTEM

Important services:

```text
subscription_service.py
subscription_checker.py
subscription_notification_service.py
subscription_reminder_service.py
subscription_token.py
```

Background task:

```text
app/tasks/subscription_task.py
```

The task periodically:

```text
subscription checker
sync service
payment expiration
```

The subscription system must keep the local database and 3x-ui client expiry synchronized.

---

# 18. CURRENT IMPORTANT DEVELOPMENT AREA

The immediate development area is:

```text
VLESS client lifecycle + 3x-ui synchronization
```

Particularly:

```text
create client
update expiry
disable/expire client
subscription renewal
subscription expiration
database ↔ 3x-ui synchronization
```

The current modified files are:

```text
app/protocols/handlers/vless.py
app/services/xui_client.py
```

These should be examined first before introducing further changes.

---

# 19. CURRENT TEST / DEBUG SCRIPTS

Available scripts:

```text
scripts/check_db.py
scripts/check_payments_schema.py
scripts/check_yoo.py
scripts/db_view.py
scripts/expire_subscription.py
scripts/init_db.py
scripts/inspect_xui.py
scripts/migrate_payments.py
scripts/seed_server.py
scripts/show_clients.py
scripts/show_subscriptions.py
scripts/test_checker.py
scripts/test_client_update.py
scripts/test_create_subscription.py
scripts/test_update_api.py
scripts/test_update_expiry.py
scripts/test_update_api.py
scripts/update_token.py
```

These scripts are development/debugging tools.

They should not become part of production business logic.

---

# 20. PRODUCTION SERVICE

Systemd service:

```text
/etc/systemd/system/justvpn.service
```

Current command:

```text
/opt/vpn-bot/.venv/bin/python /opt/vpn-bot/main.py
```

Working directory:

```text
/opt/vpn-bot
```

Restart:

```text
always
```

Logs:

```text
journalctl -u justvpn
```

---

# 21. NGINX

Current `/etc/nginx/sites-available/default` is essentially the default Nginx configuration.

It currently serves:

```text
/var/www/html
```

There is no active reverse proxy configuration for the JustVPN Backend in the current configuration.

This is an infrastructure item to address later.

---

# 22. ENVIRONMENT

Important environment variables:

```text
BOT_TOKEN
ADMIN_ID
MINIAPP_URL

XUI_API_URL
XUI_API_TOKEN

VPN_HOST
VPN_NAME
VPN_COUNTRY
VPN_WG_DNS

ENABLE_VLESS

VPN_VLESS_INBOUND
VPN_WIREGUARD_INBOUND

DATABASE_PATH

YOOKASSA_SHOP_ID
YOOKASSA_SECRET_KEY
PAYMENT_RETURN_URL

JWT_SECRET
JWT_ALGORITHM
JWT_EXPIRE_DAYS

BACKEND_API_URL
BACKEND_API_KEY

DEBUG
```

Production `.env`:

```text
/opt/vpn-bot/.env
```

Database:

```text
/opt/vpn-bot/data/vpn.db
```

---

# 23. SECURITY RULES

Never commit:

```text
.env
database files
JWT secrets
Telegram bot token
YooKassa secret
3x-ui API token
Backend API key
private VPN credentials
```

`.gitignore` already excludes:

```text
.env
*.db
*.sqlite
*.sqlite3
```

IMPORTANT:

Some old development scripts currently contain hardcoded-looking 3x-ui/API tokens.

These should be removed from source code.

If a token was exposed outside the server/repository, rotate it.

Future scripts must obtain credentials from:

```text
app.config.settings
```

or environment variables.

---

# 24. GIT STATUS AT CONTEXT SAVE

Current branch:

```text
main
```

Remote:

```text
origin
git@github.com:justmoresmile/vpn_bot.git
```

Branch is currently synchronized with:

```text
origin/main
```

Uncommitted files:

```text
app/protocols/handlers/vless.py
app/services/xui_client.py
```

Before starting a new feature:

```bash
git status
git diff -- app/protocols/handlers/vless.py
git diff -- app/services/xui_client.py
```

Do NOT discard these changes without understanding what they contain.

---

# 25. DEVELOPMENT RULES

## Rule 1 — Backend first

Business logic belongs in:

```text
app/services/
```

API exposure belongs in:

```text
app/api/routes/
```

Database access belongs in:

```text
app/repositories/
```

Protocol-specific VPN logic belongs in:

```text
app/protocols/
```

---

## Rule 2 — Clients stay thin

Telegram:

```text
UI → API
```

Mini App:

```text
UI → API
```

Android:

```text
UI → Repository → API
```

Do not duplicate subscription/payment/VPN business logic in clients.

---

## Rule 3 — Protocols stay pluggable

Do not implement VLESS using scattered:

```text
if protocol == "vless"
```

throughout the application.

Prefer:

```text
ProtocolHandler
     │
     ├── VLESSHandler
     └── WireGuardHandler
```

The purpose is to make future protocols possible without rewriting the subscription system.

---

## Rule 4 — 3x-ui is infrastructure

Application code should communicate with 3x-ui through:

```text
XUIClient
```

Do not put raw `httpx` requests to 3x-ui inside random services or Telegram handlers.

---

## Rule 5 — Database is source of application state

The database stores:

```text
user
subscription
payment
server
```

3x-ui stores the actual VPN client configuration.

Synchronization must be explicit.

---

## Rule 6 — Do not break existing clients

Before modifying:

```text
subscription API
payment API
auth API
VPN API
```

check all current consumers:

```text
Telegram Bot
Mini App
Android
Admin
```

---

# 26. CURRENT ARCHITECTURAL TARGET

The desired final structure is:

```text
                         CLIENTS
                            │
            ┌───────────────┼────────────────┐
            │               │                │
         Telegram         Mini App         Android
            │               │                │
            └───────────────┼────────────────┘
                            │
                            ▼
                     Backend API
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
       Auth             Services           Payments
                            │
              ┌─────────────┼─────────────┐
              │             │             │
           Users       Subscriptions      VPN
                                          │
                                   VPNService
                                          │
                                  ProtocolHandler
                                    │       │
                                  VLESS  WireGuard
                                    │       │
                                  XUIClient  future
                                    │
                                   3x-ui
                                    │
                                   Xray
```

---

# 27. IMMEDIATE ROADMAP

## Phase 1 — Finish VLESS lifecycle

Priority: HIGH

Verify:

* VLESS client creation
* UUID generation
* email generation
* inbound selection
* subscription URL generation
* client expiry
* update expiry
* disable expired client
* renewal
* duplicate protection
* database synchronization

---

## Phase 2 — Stabilize XUIClient

Priority: HIGH

Review:

```text
app/services/xui_client.py
```

Make sure it has clear methods for:

```text
login/authentication if required
get_inbounds
get_inbound
create_client
update_client
delete/disable client
close
```

Avoid endpoint guessing in production code.

Document the exact 3x-ui 3.6.0 API behavior.

---

## Phase 3 — Stabilize SubscriptionService

Priority: HIGH

Subscription creation should follow one controlled flow:

```text
User
 ↓
SubscriptionService
 ↓
select server
 ↓
select protocol
 ↓
ProtocolHandler
 ↓
3x-ui
 ↓
save subscription
 ↓
return configuration
```

---

## Phase 4 — Payment → Subscription integration

Priority: HIGH

Verify the complete flow:

```text
Telegram/MiniApp
       ↓
purchase
       ↓
YooKassa
       ↓
webhook
       ↓
PaymentService
       ↓
SubscriptionService
       ↓
VPNService
       ↓
XUIClient
```

---

## Phase 5 — Subscription expiration

Priority: HIGH

Expected behavior:

```text
subscription expires
       ↓
checker detects expiration
       ↓
local status updated
       ↓
VPN client disabled/expired
       ↓
user notification
```

---

## Phase 6 — Public subscription system

Priority: HIGH

VLESS subscription URLs should be stable and safe.

The public subscription endpoint should:

```text
validate subscription token
check subscription status
check expiry
generate current configuration
return VLESS subscription
```

The user should not need to know anything about 3x-ui.

---

## Phase 7 — Mini App

Priority: MEDIUM

Continue the existing Mini App.

Main areas:

```text
Home
VPN status
Subscription
Buy
Profile
Settings
Support
```

Current theme system should be preserved.

---

## Phase 8 — Android VLESS support

Priority: MEDIUM

After backend VLESS is stable:

```text
Backend API
     ↓
Android
     ↓
VLESS configuration
     ↓
Android VPN implementation
```

WireGuard support remains available.

Do not remove existing WireGuard architecture.

---

## Phase 9 — Production infrastructure

Priority: MEDIUM

Later configure:

```text
HTTPS
Nginx reverse proxy
systemd
health checks
logging
backup
database backup
monitoring
```

---

# 28. WHAT NOT TO DO

Do not:

* rewrite the project from scratch
* replace SQLite without a reason
* remove WireGuard
* remove the protocol plugin architecture
* move business logic into Telegram
* make Mini App communicate directly with 3x-ui
* make Android communicate directly with 3x-ui
* hardcode API credentials
* create a second independent subscription system
* create a second payment system
* duplicate user state between clients
* bypass repositories with random SQL
* bypass XUIClient with raw requests
* introduce a new architecture without updating this document

---

# 29. CURRENT PRIORITY

The next conversation/task should start here:

```text
1. Inspect current changes:
   app/protocols/handlers/vless.py
   app/services/xui_client.py

2. Understand exactly what was changed.

3. Test the current VLESS/XUI client update flow.

4. Stabilize XUIClient API.

5. Stabilize VLESSHandler.

6. Verify subscription creation.

7. Verify subscription renewal.

8. Verify expiration.

9. Verify 3x-ui synchronization.

10. Commit stable changes.

11. Update PROJECT.md.
```

---

# 30. STANDARD CONTINUATION PROCEDURE

When starting a new development chat, provide:

```text
This is the JustVPN project.

Read PROJECT.md first.

Continue development from the current state.
Do not redesign the architecture unless explicitly requested.

Current priority:
[describe task]
```

Then provide actual command output when needed.

The assistant should use `PROJECT.md` as the project source of truth, while the actual repository remains the source of truth for code.

---

# 31. PROJECT STATE PRINCIPLE

There are two sources of truth:

```text
CODE
+
PROJECT.md
```

Code determines what actually exists.

`PROJECT.md` determines:

* architectural decisions
* intended architecture
* development rules
* roadmap
* current priorities
* decisions that must not be accidentally reverted

When these disagree:

```text
actual code wins for current implementation
PROJECT.md wins for intended architecture
```

The discrepancy should then be resolved explicitly.

---

# 32. VERSION HISTORY

## Version 0.9

Existing JustVPN platform state before the current VLESS stabilization phase.

Included:

* FastAPI Backend
* Telegram Bot
* SQLite
* YooKassa
* 3x-ui integration
* protocol handler architecture
* VLESS handler
* WireGuard handler
* Mini App
* Android client foundation
* authentication
* subscriptions
* payments
* background subscription checker

---

# 33. NEXT MILESTONE

The next milestone is:

> **Stable production VLESS subscription lifecycle through Backend API and 3x-ui.**

Definition of done:

```text
User
 ↓
purchase
 ↓
payment confirmed
 ↓
subscription created
 ↓
VLESS client created in 3x-ui
 ↓
configuration returned
 ↓
client connects
 ↓
renewal extends expiry
 ↓
expiry disables access
 ↓
all states synchronized
```

Only after this lifecycle is reliable should major new client functionality be added.

---

# 34. END OF CURRENT CONTEXT

Current server:

```text
/opt/vpn-bot
```

Current production service:

```text
justvpn.service
```

Current VPN panel:

```text
3x-ui 3.6.0
```

Current primary protocol:

```text
VLESS
```

Current secondary/native protocol:

```text
WireGuard
```

Current database:

```text
SQLite
```

Current API:

```text
FastAPI
```

Current clients:

```text
Telegram Bot
Mini App
Android
```

Current immediate work:

```text
VLESS + XUIClient + subscription lifecycle
```

**Do not restart the project from the beginning. Continue from this state.**

